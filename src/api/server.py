"""FastAPI server for the RANGE//LAB interactive compiler workbench.

Provides REST API endpoints for compiler execution, built-in examples,
custom simulations, and static asset serving for the web frontend.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import traceback
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.api.serializer import serialize_compilation_result
from src.backend.simulator import SimulatorError
from src.diagnostics.errors import CompilerError, LexError, ParseError, SemanticError
from src.pipeline import compile_source

# Locate directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "examples"
WEB_DIST_DIR = BASE_DIR / "web" / "dist"


class CompileRequest(BaseModel):
    source: str = Field(..., description="Custom .qc source code")
    widen_after: int = Field(3, ge=1, le=100, description="Loop widening threshold")
    narrow: bool = Field(False, description="Enable iterative narrowing phase")
    prune_unreachable: bool = Field(False, description="Prune statically unreachable blocks")
    inputs: Optional[List[Any]] = Field(default=None, description="Optional runtime input values")


class SimulateRequest(BaseModel):
    source: str = Field(..., description="Custom .qc source code")
    widen_after: int = Field(3, ge=1, le=100)
    narrow: bool = Field(False)
    inputs: List[Any] = Field(default_factory=list, description="Input values for simulation")


class ExampleItem(BaseModel):
    id: str
    name: str
    category: str
    description: str
    source: str
    narrow: bool = False
    widen_after: int = 3
    prune_unreachable: bool = False


# Curated, comprehensive set of built-in teaching-scale examples
BUILTIN_EXAMPLES: List[Dict[str, Any]] = [
    {
        "id": "safe_arithmetic",
        "name": "Provably Safe Arithmetic",
        "category": "Basic Arithmetic",
        "description": "Standard addition where x=10 and y=20 infer z=[30, 30], provably within signed INT8 [-128, 127] bounds and rewritten to INT8.",
        "source": """int x = 10;
int y = 20;
int z = x + y;
print z;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "overflow_rejection",
        "name": "Direct Overflow Rejection",
        "category": "Safety Boundaries",
        "description": "Addition of 100 + 30 yields 130 > 127, safely detected as exceeding signed INT8 boundary and retained in original 32-bit int.",
        "source": """int x = 100;
int y = 30;
int z = x + y;
print z;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "non_integral_rejection",
        "name": "Non-Integral Float Rejection",
        "category": "Safety Boundaries",
        "description": "Float variables and fractional computations (3.5) are soundly rejected from INT8 quantization to preserve fractional semantics.",
        "source": """float x = 10.0;
float y = 3.5;
float z = x + y;
print z;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "if_else_phi",
        "name": "Control Flow & Phi Merging",
        "category": "Control Flow",
        "description": "Branching construct demonstrating SSA phi-node generation, edge refinement, unreachable false branch detection, and safe merge.",
        "source": """int x = 10;
int y = 20;
int max = 0;
if (x > y) {
    max = x;
} else {
    max = y;
}
print max;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "branch_refinement",
        "name": "Branch Condition Refinement",
        "category": "Refinement",
        "description": "Relational condition x >= 10 refines the variable interval along the true branch edge, detecting the false branch as unreachable.",
        "source": """int x = 15;
int y = 0;
if (x >= 10) {
    y = x - 5;
} else {
    y = x + 5;
}
print y;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "bounded_loop_counter",
        "name": "Bounded Loop with Narrowing",
        "category": "Loop Analysis",
        "description": "Loop counter i starts at 0 and increments while i < 10. With narrowing enabled, the counter safely converges to [0, 10] and is quantized to INT8.",
        "source": """int i = 0;
while (i < 10) {
    i = i + 1;
}
print i;
""",
        "narrow": True,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "while_loop_widening",
        "name": "Loop Widening Fallback",
        "category": "Loop Analysis",
        "description": "Loop with expanding accumulator. Widening extrapolates the unbounded sum to UNKNOWN, preventing unsafe overflow.",
        "source": """int x = 5;
int sum = 0;
while (x > 0) {
    sum = sum + x;
    x = x - 1;
}
print sum;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "stabilizing_loop",
        "name": "Stabilizing Oscillating Loop",
        "category": "Loop Analysis",
        "description": "Loop where state variable x = 1 - x toggles between 0 and 1, stabilizing within abstract domain sweeps without widening to UNKNOWN.",
        "source": """int x = 0;
int n = 4;
while (n > 0) {
    x = 1 - x;
    n = n - 1;
}
print x;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "intermediate_overflow",
        "name": "Intermediate Overflow Blocking",
        "category": "Safety Boundaries",
        "description": "Intermediate expression c = 100 + 50 overflows INT8 (150 > 127). Even though d = c - 50 lands back in [100, 100], downstream quantization is soundly blocked.",
        "source": """int a = 100;
int b = 50;
int c = a + b;
int d = c - 50;
print d;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "boundary_fit_exact",
        "name": "Exact Signed INT8 Limits",
        "category": "Safety Boundaries",
        "description": "Verifies exact signed INT8 boundary limits: -128 (lower bound) and 127 (upper bound) are proven safe and quantized.",
        "source": """int min_val = -128;
int max_val = 127;
print min_val;
print max_val;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "unsupported_op_rejection",
        "name": "Unsupported Operator Rejection",
        "category": "Supported Ops",
        "description": "Division '/' produces a float result that is not supported for INT8 rewriting and is safely kept in its original type.",
        "source": """int a = 20;
int b = 4;
float c = a / b;
print c;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
    {
        "id": "edge_linear_transform",
        "name": "Edge AI Linear Transform",
        "category": "Neural Transform",
        "description": "Typical quantized edge inference node computing y = W*x + b with bounded integer activation input x in [0, 10], W=5, b=12.",
        "source": """int x = 8;
int w = 5;
int b = 12;
int y = w * x + b;
print y;
""",
        "narrow": False,
        "widen_after": 3,
        "prune_unreachable": False,
    },
]


app = FastAPI(
    title="RANGE//LAB API",
    description="Backend API for Range-Aware Edge AI Quantization Compiler Workbench",
    version="1.0.0",
)

# CORS middleware for local Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "online",
        "app": "RANGE//LAB",
        "version": "1.0.0",
        "compiler": "Range-Aware Edge AI Quantization Compiler",
        "course": "BCSE307L — Compiler Design",
    }


@app.get("/api/examples")
async def get_examples() -> List[Dict[str, Any]]:
    """Return all built-in .qc example benchmarks."""
    return BUILTIN_EXAMPLES


@app.post("/api/compile")
async def compile_code(req: CompileRequest) -> Dict[str, Any]:
    """Compile custom .qc source and return complete pipeline analysis and simulation."""
    if not req.source.strip():
        return {
            "success": False,
            "error": {
                "stage": "Input",
                "message": "Source code cannot be empty.",
                "line": 1,
                "col": 1,
            },
        }

    try:
        res = compile_source(
            source=req.source,
            widen_after=req.widen_after,
            inputs=req.inputs or [],
            run_simulation=True,
            narrow=req.narrow,
            prune_unreachable=req.prune_unreachable,
        )
        return serialize_compilation_result(res)

    except LexError as e:
        loc = getattr(e, "loc", None)
        return {
            "success": False,
            "error": {
                "stage": "Lexer",
                "message": str(e),
                "line": loc.line if loc else None,
                "col": loc.column if loc else None,
            },
        }
    except ParseError as e:
        loc = getattr(e, "loc", None)
        return {
            "success": False,
            "error": {
                "stage": "Parser",
                "message": str(e),
                "line": loc.line if loc else None,
                "col": loc.column if loc else None,
            },
        }
    except SemanticError as e:
        loc = getattr(e, "loc", None)
        return {
            "success": False,
            "error": {
                "stage": "Semantic Analysis",
                "message": str(e),
                "line": loc.line if loc else None,
                "col": loc.column if loc else None,
            },
        }
    except SimulatorError as e:
        return {
            "success": False,
            "error": {
                "stage": "Simulator",
                "message": str(e),
                "line": None,
                "col": None,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "stage": "Internal Compiler Exception",
                "message": f"{type(e).__name__}: {str(e)}",
                "line": None,
                "col": None,
                "details": traceback.format_exc(),
            },
        }


@app.post("/api/simulate")
async def simulate_code(req: SimulateRequest) -> Dict[str, Any]:
    """Run program simulation with custom inputs."""
    try:
        res = compile_source(
            source=req.source,
            widen_after=req.widen_after,
            inputs=req.inputs,
            run_simulation=True,
            narrow=req.narrow,
        )
        if res.simulation:
            return {
                "success": True,
                "original_output": res.simulation.original_output,
                "quantized_output": res.simulation.quantized_output,
                "is_equivalent": res.simulation.is_equivalent,
                "error": res.simulation.error,
            }
        return {"success": False, "error": "Simulation could not be executed."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Serve static web frontend if built
if WEB_DIST_DIR.exists() and (WEB_DIST_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(WEB_DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        target = WEB_DIST_DIR / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(WEB_DIST_DIR / "index.html")


def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Entry point to start the server via Uvicorn."""
    import uvicorn
    uvicorn.run("src.api.server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run()
