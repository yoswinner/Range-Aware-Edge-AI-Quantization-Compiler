# Project Reviews Archive — Comprehensive Inventory and Index

**Project:** Range-Aware Edge AI Quantization Compiler  
**Repository Root:** `C:\Coding\GenAI\Projects\Range-Aware-Edge-AI-Quantization-Compiler`  
**Archive Root:** `C:\Coding\GenAI\Projects\Range-Aware-Edge-AI-Quantization-Compiler\Project_Reviews_Archive`  
**Last Updated:** October 19, 2026 (Final Deduplication & Verification)  
**Status:** Complete, Fully Deduplicated & Verified Byte-for-Byte  

---

## 1. Overview and Archive Purpose

This directory serves as the centralized, structured archive of all academic review deliverables, reports, presentations, verification evidence packs, demonstration artifacts, and shared benchmark programs spanning **Review 1**, **Review 2**, and **Review 3** for the *Range-Aware Edge AI Quantization Compiler* project.

All files contained within this archive are **exact byte-for-byte copies** of their canonical originals within the repository. Following the deduplication audit:
- Every unique document, presentation, evidence pack, benchmark program, and high-resolution screenshot is preserved in its directly accessible, uncompressed format.
- Redundant ZIP containers (`RANGE-LAB-Screenshots.zip` and `Review3_Claude_Reference_Pack.zip`) whose contents are 100% duplicated by preserved standalone files were pruned from the archive to ensure zero internal duplication.
- Redundant parent-folder duplicates in the workspace (`artifacts/RANGE-LAB-Screenshots.zip` and `artifacts/screenshot_gallery.md`) were removed while preserving canonical versions in `artifacts/screenshots/`.
- The temporary working patch `files/review3_repo_working_copy_changes.patch` was pruned from `files/` after being merged to `master` and is preserved here as a historical review artifact.

---

## 2. Directory Hierarchy

```
Project_Reviews_Archive/
│
├── Review_1/
│   └── Presentations_and_PDFs/
│       ├── Review_1_plan.pdf
│       └── Review_1_ppt.pdf
│
├── Review_2/
│   ├── Reports_and_PDFs/
│   └── Presentations_and_PPTs/
│       └── Review_2_Presentation.pptx
│   └── Supporting_Documents_and_Progress/
│       ├── CONSISTENCY_CHECK.md
│       ├── IMPLEMENTATION_STATUS.md
│       ├── PRESENTATION_UPDATE_NOTES.md
│       ├── REPORT_UPDATE_NOTES.md
│       └── STAGE_EVIDENCE.md
│
├── Review_3/
│   ├── Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler.docx       [OFFICIAL FINAL REPORT - EDITABLE]
│   ├── Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler_preview.pdf [OFFICIAL FINAL REPORT - PREVIEW]
│   ├── Evidence_Packs_and_Catalogs/
│   │   ├── Review3_Implementation_Evidence_Pack.docx
│   │   ├── Review3_Implementation_Evidence_Pack.md
│   │   ├── RANGE_LAB_Screenshot_Catalog.docx
│   │   └── RANGE_LAB_Screenshot_Catalog.md
│   ├── Screenshots_and_Demonstrations/
│   │   ├── 01-main-workbench.png
│   │   ├── 02-int8-safety.png
│   │   ├── 03-overflow-rejection.png
│   │   ├── 04-ssa-inspector-z1.png
│   │   ├── 05-ssa-inspector-x1.png
│   │   ├── 06-control-flow-graph.png
│   │   ├── 07-simulation-equivalence.png
│   │   ├── 08-loop-narrowing.png
│   │   ├── 09-lexer-ast.png
│   │   ├── 10-tac-ssa-phi.png
│   │   ├── 11-range-analysis.png
│   │   ├── 12-branch-refinement.png
│   │   ├── 13-quantized-ir-diagnostics.png
│   │   ├── 14-verification-results.png
│   │   └── screenshot_gallery.md
│   └── Handoff_and_Packaging/
│       ├── CLAUDE_REVIEW3_HANDOFF.md
│       ├── PACKAGE_INVENTORY.txt
│       └── review3_repo_working_copy_changes.patch
│
├── Shared_Project_Materials/
│   ├── Architecture_and_Overview/
│   │   └── README.md
│   └── Benchmark_Programs/
│       ├── bounded_loop.qc
│       ├── branch_refine.qc
│       ├── if_else_phi.qc
│       ├── non_integral_rejection.qc
│       ├── overflow_rejection.qc
│       ├── safe_arithmetic.qc
│       ├── stabilizing_loop.qc
│       ├── unsupported_division.qc
│       └── while_loop.qc
│
└── Archive_Index.md
```

---

## 3. Review 1 Deliverables Inventory (2 Files)

**Milestone Focus:** Initial project proposal, architecture planning, theoretical framework, syllabus mapping, and work breakdown.

| Filename | Canonical Project Path | Format | Size (Bytes) | SHA-256 Hash | Purpose & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Review_1_plan.pdf` | `docs/review/Review_1_plan.pdf` | PDF Document | 661,998 | `B2A5047F0FD2657DAABCEFAE865BA2361EE9B4B8EE4FF2830B58FF3C056FE5E0` | Initial project plan and formal proposal report detailing planned compiler passes, static range analysis, and INT8 safety model. |
| `Review_1_ppt.pdf` | `docs/review/Review_1_ppt.pdf` | PDF Export | 1,196,693 | `47DB5C90711154500804FAFAE38B1C8D4DF1CF4D50CC88402D0287CC0C279CD5` | Slide presentation export for the initial project defense and review. |

*Notes on Review 1:*
- No editable Word (`.docx`) or PowerPoint (`.pptx`) source files exist in the repository; only the final PDF exports are preserved.
- No separate standalone screenshots were generated during Review 1 as implementation was in the proposal stage.

---

## 4. Review 2 Deliverables Inventory (7 Files)

**Milestone Focus:** 60% implementation milestone, core compiler pipeline validation (Lexer, Parser, AST, Semantic, TAC, CFG, SSA, Fixed-Point Iteration, Loop Widening, INT8 Safety Decision, Simulator Backend).

| Filename | Canonical Project Path | Format | Size (Bytes) | SHA-256 Hash | Purpose & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Review_2_Report.pdf` | `docs/review/Review_2_Report.pdf` | PDF Document | 731,628 | `37C8B786EABEA52BA4244C713242E61F8D98C12658CE6EDF76A036E4D1409CFA` | Midterm 60% progress report detailing implementation of compiler passes, SSA dominance frontiers, Kleene fixed-point iteration, and 20 passing unit tests. |
| `Review_2_Presentation.pptx` | `docs/review/Review_2_Presentation.pptx` | PowerPoint Presentation | 1,582,813 | `3DD8FAA7D7813438E395F40D8C8FFDCE9508BFD32C5E897CD663E206A26B74A5` | Editable PowerPoint presentation slides with architecture diagrams, pipeline walkthrough, and initial benchmark results. |
| `CONSISTENCY_CHECK.md` | `docs/progress/60-percent/CONSISTENCY_CHECK.md` | Markdown | 2,240 | `5AB4C52B6E73A221AB221FD80B68C22F2625245CCF8D161BC7E6F3924DE16C63` | Audit document verifying that implemented code aligns with theoretical specifications in the Review reports. |
| `IMPLEMENTATION_STATUS.md` | `docs/progress/60-percent/IMPLEMENTATION_STATUS.md` | Markdown | 5,829 | `C4F0FDD857845A4F95AB2E50B2D46983A7FDF81A31C8244CDD858CF574B20C6E` | Compiler stages implementation audit, unit test results (20/20 passing), and representative E2E outputs. |
| `PRESENTATION_UPDATE_NOTES.md` | `docs/progress/60-percent/PRESENTATION_UPDATE_NOTES.md` | Markdown | 842 | `E476AC7CD442DB3D918184B9FCB170B92B08FE831E0594ECF615AF0EB6014CA7` | Guidance notes on transitioning presentation slides from proposed design to verified implementation evidence. |
| `REPORT_UPDATE_NOTES.md` | `docs/progress/60-percent/REPORT_UPDATE_NOTES.md` | Markdown | 1,850 | `3D1CB3C01AF5E67CFBEE38619DFBE5E048A452BFED41D9E1BDE1A63920B2F2E4` | Detailed section-by-section notes for updating the Review 1 plan report into the Review 2 milestone report. |
| `STAGE_EVIDENCE.md` | `docs/progress/60-percent/STAGE_EVIDENCE.md` | Markdown | 3,706 | `01D7135B8201B9DB574F1617C468FE029304F2E45C4B40BA6771F3699D859F58` | Stage-by-stage implementation evidence logging inputs, outputs, and validation metrics for each pass. |

*Notes on Review 2:*
- Early working drafts (`Review_2_Report.md`, `Review_2_Report_Final.docx`, `Review_2_ppt.pptx`) existed in Git commit `8a6451e` and were superseded and replaced by `Review_2_Report.pdf` and `Review_2_Presentation.pptx` in commit `755ced2`.

---

## 5. Review 3 Deliverables Inventory (24 Files)

**Milestone Focus:** Final academic capstone submission, comprehensive project report, formal evidence packs, interactive RANGE//LAB visual compiler workbench, reproducible evaluation benchmark suite (12 benchmarks, 141 tests), and post-merge verification.

### 5.1 Official Final Report Deliverables (2 Files)

> [!IMPORTANT]
> The two files below represent the **official, audited final deliverables** for Review 3 submission, matching the verified GitHub `master` branch commit (`8ed3083519f551470b9c5df41b8d479dac03d834`).

| Filename | Canonical Project Path | Format | Size (Bytes) | SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler.docx`** | `files/Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler.docx` | Word Document (.docx) | 4,895,425 | `9D6B06C88FEDD7C9BF17C0941173C7B5115B50A31B450AC3A7003B91DD33DA36` | **Final Audited Report (Editable)** |
| **`Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler_preview.pdf`** | `files/Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler_preview.pdf` | PDF Document | 3,264,766 | `63167A525605165C530A90900CB1190C67321C70CA1DDCCAAE01099EAD1706EE` | **Final Audited Report (PDF Preview)** |

### 5.2 Evidence Packs & Catalogs (4 Files)

| Filename | Canonical Project Path | Format | Size (Bytes) | SHA-256 Hash | Purpose & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Review3_Implementation_Evidence_Pack.docx` | `docs/review3/Review3_Implementation_Evidence_Pack.docx` | Word Document (.docx) | 66,838 | `68ACB940193265C0AEA145C7A92DE826A76E1DA98696F6392D66C93C32F715BD` | Formal academic evidence pack documenting AST, TAC, CFG, SSA, fixed-point iteration, and quantization transformation. |
| `Review3_Implementation_Evidence_Pack.md` | `docs/review3/Review3_Implementation_Evidence_Pack.md` | Markdown | 63,058 | `F0B922A14E186D92170D982C7E9C88C02BEE141440BEE794C23DCF0E26D81145` | Markdown source version of the formal implementation evidence pack. |
| `RANGE_LAB_Screenshot_Catalog.docx` | `docs/review3/RANGE_LAB_Screenshot_Catalog.docx` | Word Document (.docx) | 3,250,083 | `E45028F28A81AEC0D18999A07D7FFC87CFD5AF2824C27DA915CF0C44031B05FD` | Formal screenshot catalog with captions and technical explanations of all 14 visual compiler lab workbench screens. |
| `RANGE_LAB_Screenshot_Catalog.md` | `docs/review3/RANGE_LAB_Screenshot_Catalog.md` | Markdown | 29,666 | `C90892E04E370013FC8162FF305C7DF7AE0EB85F8CC59E27A2BA2E4B856338FD` | Markdown source version of the screenshot catalog. |

### 5.3 Screenshots & Demonstration Evidence (15 Files)

| Filename | Canonical Project Path | Size (Bytes) | SHA-256 Hash | Demonstrated Compiler Feature |
| :--- | :--- | :--- | :--- | :--- |
| `01-main-workbench.png` | `artifacts/screenshots/01-main-workbench.png` | 188,222 | `516951CE67572990F81DD6303FE069FEE09B4E38CA58A009C7954BCB1541D8B4` | Full RANGE//LAB workbench overview with editor and stage navigation |
| `02-int8-safety.png` | `artifacts/screenshots/02-int8-safety.png` | 274,292 | `89DC66A909F40CEED3206248A3BF85E5F69F8B5C0EF646453A81D67B25988185` | INT8 safety verification view with bounds check `[-128, 127]` |
| `03-overflow-rejection.png` | `artifacts/screenshots/03-overflow-rejection.png` | 294,023 | `269EE67A76B913ED707EFBD8E1F73F5A8E891EEBA6D8FF987D70A0F45424564E` | Conservative rejection on arithmetic overflow (`130 > 127`) |
| `04-ssa-inspector-z1.png` | `artifacts/screenshots/04-ssa-inspector-z1.png` | 346,064 | `055D6C12B7AE97DA501106C3FF7E4DA9090ED6052E10978EBE5927513C3DC2A4` | Deep variable inspection modal for SSA variable `z.1` |
| `05-ssa-inspector-x1.png` | `artifacts/screenshots/05-ssa-inspector-x1.png` | 320,298 | `F910663C60B3CE3E29D5255A2F2BDE5EC74D6C4F773A506385B2DCBFFFEA47A7` | Deep variable inspection modal for SSA variable `x.1` |
| `06-control-flow-graph.png` | `artifacts/screenshots/06-control-flow-graph.png` | 212,852 | `BA128725A7A7CF9E496E512A1F45ECFBD6F3C012B58DC8E9D57C5EC30A75E5FF` | Interactive React Flow CFG with block boundaries and edge types |
| `07-simulation-equivalence.png` | `artifacts/screenshots/07-simulation-equivalence.png` | 212,100 | `04999CA73B7FBE6F385018697E0C06E393BA81B34828E46FE8F8CD53BE5FA707` | Side-by-side simulator execution (Original FP32 vs Quantized INT8) |
| `08-loop-narrowing.png` | `artifacts/screenshots/08-loop-narrowing.png` | 200,164 | `0C2BC88203DD785E6C7C48C1014CD99A595874404EF285A2441995A1E5C1CD0D` | Loop narrowing and fixed-point stabilization evaluation |
| `09-lexer-ast.png` | `artifacts/screenshots/09-lexer-ast.png` | 206,875 | `DE67283D3C33FCAD13E70752F3908051E64DAFDEDBA5C2D2702758252C327898` | Lexer token stream and syntax tree hierarchy viewer |
| `10-tac-ssa-phi.png` | `artifacts/screenshots/10-tac-ssa-phi.png` | 193,921 | `F0CB6B6063A4334B02DB071EA1C74E06A80DF32C034177241A70ED23956F1470` | 3-Address Code and SSA conversion with dominance frontier Phi nodes |
| `11-range-analysis.png` | `artifacts/screenshots/11-range-analysis.png` | 201,568 | `D29B133A579895D5EAF7196FA9CEBC950C2DF2510A2B43D55C7026A5F5871D62` | Static interval propagation table and integrality analysis |
| `12-branch-refinement.png` | `artifacts/screenshots/12-branch-refinement.png` | 231,702 | `1945E770E3E479AE0D6F70D9E743F07E3FA3F6C341C771B8AC5297241857970C` | Conditional branch condition refinement and dead-block pruning |
| `13-quantized-ir-diagnostics.png` | `artifacts/screenshots/13-quantized-ir-diagnostics.png` | 208,103 | `3280CB62E479FDBC894EE4B901C46E3F40E9F2410D6F1846A04B141BCF0EB715` | Retyped INT8 SSA instructions alongside line-by-line compiler diagnostics |
| `14-verification-results.png` | `artifacts/screenshots/14-verification-results.png` | 286,877 | `4152AC4D6AD07B3E19AB62327D16A46761A0C06152B3512CC2A2B7A821BFEC68` | Full automated test suite results (141 tests, 0 failures, 12 benchmarks) |
| `screenshot_gallery.md` | `artifacts/screenshots/screenshot_gallery.md` | 4,656 | `C485439C9AF04EC551A91F1CB8806DE8F0449A0C9CF68449EEDB8EF0B5514FC0` | Markdown gallery layout displaying thumbnail previews and descriptions |

### 5.4 Handoff & Historical QA Patch (3 Files)

| Filename | Canonical Project Path | Format | Size (Bytes) | SHA-256 Hash | Purpose & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CLAUDE_REVIEW3_HANDOFF.md` | `docs/review3/CLAUDE_REVIEW3_HANDOFF.md` | Markdown | 20,851 | `9C8ADF594280EDFDCA84140DE9D490B6002A46762319EC01594A55ACF5DCEB02` | Technical briefing document provided to Claude for authoring the Review 3 report, containing benchmark outputs, test counts, and theoretical bounds. |
| `PACKAGE_INVENTORY.txt` | `docs/review3/PACKAGE_INVENTORY.txt` | Plain Text | 7,421 | `E1E49CF41D0B388F035D2E4A4CDCEB93B24F181313F217FD1860BE29606132D5` | Manifest of all generated assets, test logs, and figures comprising the Review 3 evidence submission. |
| `review3_repo_working_copy_changes.patch` | Archived Historical Record | Git Patch | 7,210 | `B7BD8CE44BAE52865729BAA01D8CA932BF7C1FDD0C601A9268AD9F8C0EAB0F9A` | Audited patch implementing dead-block unreachable pruning and simulator label fixes, merged into `master`. Preserved here as an uncompressed historical review artifact. |

---

## 6. Shared Project Materials (10 Files)

**Purpose:** Assets, system documentation, and program benchmarks referenced across multiple review phases.

| Filename | Canonical Project Path | Format | Size (Bytes) | SHA-256 Hash | Purpose & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `README.md` | `README.md` | Markdown | 17,353 | `57BF74CB1221371AC8E35201D8DC4C72B97A0A9D0A7F54B069273C2C5E778E29` | Complete project documentation: architecture diagrams, stage-by-stage pipelines, mathematical formulation, verification commands, and known limitations. |
| `bounded_loop.qc` | `examples/bounded_loop.qc` | `.qc` Source | 59 | `EC478A2C66722070BE1EE25A826BBA45F3DC46FDE083A8C63EBA67104CF93FF6` | Benchmark evaluating loop counter bounded within INT8 range. |
| `branch_refine.qc` | `examples/branch_refine.qc` | `.qc` Source | 100 | `155D8941B7D1EA0A6E328475997232239BEEB3D3DEFA9F0555610DEEB9505F0F` | Benchmark evaluating path-sensitive branch condition interval refinement. |
| `if_else_phi.qc` | `examples/if_else_phi.qc` | `.qc` Source | 111 | `FBBED0A92DD3430E6F321AEFC92B28B36CF6B07469B56187766A7D9D3F9514BC` | Benchmark evaluating conditional branch joins with SSA Phi node interval merges. |
| `non_integral_rejection.qc` | `examples/non_integral_rejection.qc` | `.qc` Source | 61 | `0D25DDC91E9D6229FD4C3A005B17B0F3A2EDF03386D2C97AE9E1E4C7A398246E` | Benchmark demonstrating conservative rejection of floating-point fractional values. |
| `overflow_rejection.qc` | `examples/overflow_rejection.qc` | `.qc` Source | 53 | `021AC456505FB5B0F93A865AD7571E86E202FEFE511D8982D554D8271DA8FFB7` | Benchmark demonstrating rejection of integer arithmetic exceeding `127`. |
| `safe_arithmetic.qc` | `examples/safe_arithmetic.qc` | `.qc` Source | 52 | `7ECB9DBB79707D3E5BC879A214643B9D9AE543022B8C65FBEB7C72A0D8D56A4F` | Benchmark demonstrating 100% INT8 safety qualification on safe integer operations. |
| `stabilizing_loop.qc` | `examples/stabilizing_loop.qc` | `.qc` Source | 241 | `BA529C53870D1E0FE2E7684DBDF082DE8A1ACD9FCBC2FA9B43FD46C7EBF9456F` | Benchmark evaluating multi-iteration loop stabilization before widening threshold. |
| `unsupported_division.qc` | `examples/unsupported_division.qc` | `.qc` Source | 262 | `A58CBCA047E31DCBF48495BAC1F568C339F5774E12F6C7D085DCBFFB3DAFF16B` | Benchmark evaluating conservative rejection when divisor interval contains or straddles zero. |
| `while_loop.qc` | `examples/while_loop.qc` | `.qc` Source | 98 | `2E1030507017EB0208AF0FCB8919A321FD0A4FD4A66B136C45F42BE39C6BC4FA` | Benchmark evaluating conservative UNKNOWN fallback under loop widening. |

---

## 7. Deduplication & Storage Audit

### 7.1 Confirmed Redundant Files Removed
1. **`Project_Reviews_Archive/Review_3/Screenshots_and_Demonstrations/RANGE-LAB-Screenshots.zip`**
   - **Removal Rationale:** 100% duplicate of the 14 standalone PNG files preserved directly in `Screenshots_and_Demonstrations/`. Canonical ZIP preserved in `artifacts/screenshots/RANGE-LAB-Screenshots.zip`.
2. **`Project_Reviews_Archive/Review_3/Handoff_and_Packaging/Review3_Claude_Reference_Pack.zip`**
   - **Removal Rationale:** All 20 entries (`CLAUDE_REVIEW3_HANDOFF.md`, evidence packs, catalogs, and 14 screenshots) are preserved as standalone files within `Review_3/`. Canonical ZIP preserved in `docs/review3/Review3_Claude_Reference_Pack.zip`.
3. **`artifacts/RANGE-LAB-Screenshots.zip`**
   - **Removal Rationale:** Redundant parent-folder duplicate. Canonical copy retained at `artifacts/screenshots/RANGE-LAB-Screenshots.zip`.
4. **`artifacts/screenshot_gallery.md`**
   - **Removal Rationale:** Redundant parent-folder duplicate. Canonical copy retained at `artifacts/screenshots/screenshot_gallery.md`.
5. **`files/review3_repo_working_copy_changes.patch`**
   - **Removal Rationale:** Redundant temporary working file (already merged to `master`). Preserved solely in `Project_Reviews_Archive/Review_3/Handoff_and_Packaging/`.

### 7.2 Intentionally Retained Pairs
1. **Official Final Deliverables:**
   - `files/Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler.docx` (Tracked on `master`).
   - `Project_Reviews_Archive/Review_3/Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler.docx` (Archived, exact SHA-256 match `9D6B06C88FEDD7C9BF17C0941173C7B5115B50A31B450AC3A7003B91DD33DA36`).
2. **Official Final PDF Previews:**
   - `files/Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler_preview.pdf` (Tracked on `master`).
   - `Project_Reviews_Archive/Review_3/Review3_Project_Report_Range_Aware_Edge_AI_Quantization_Compiler_preview.pdf` (Archived, exact SHA-256 match `63167A525605165C530A90900CB1190C67321C70CA1DDCCAAE01099EAD1706EE`).

### 7.3 Retained Archives with Unique Material
- **None inside `Project_Reviews_Archive/`**: Every single piece of review material is available in standalone, uncompressed, directly readable and diffable formats.
- Outside the archive, the canonical ZIP containers remain preserved at `artifacts/screenshots/RANGE-LAB-Screenshots.zip` and `docs/review3/Review3_Claude_Reference_Pack.zip` for full historical completeness.

---

## 8. Summary File Counts

| Archive Category | Number of Files | Key Contents |
| :--- | :---: | :--- |
| **Review 1** | **2** | Proposal plan PDF, presentation slides export PDF |
| **Review 2** | **7** | 60% progress report PDF, presentation PPTX, 5 progress & audit documents |
| **Review 3** | **24** | Audited final report DOCX & preview PDF, 4 evidence packs/catalogs, 14 screenshots, gallery MD, handoff MD, inventory TXT, historical patch |
| **Shared Project Materials** | **10** | Global architecture `README.md`, 9 benchmark `.qc` programs |
| **Archive Documentation** | **1** | `Archive_Index.md` (this file) |
| **TOTAL IN ARCHIVE** | **44** | **Zero redundant internal duplicates; fully verified** |

---

## 9. Observations, Historical Context & Disclosures

1. **Faculty Feedback & Rubric Sheets:** No external faculty feedback rubrics, grading sheets, or written evaluation forms were found in the project directory. If physical or LMS feedback sheets exist, they can be added to the appropriate review subfolder.
2. **Review 1 Editable Source Files:** Review 1 materials exist solely as exported PDFs (`Review_1_plan.pdf` and `Review_1_ppt.pdf`). No pre-export `.docx` or `.pptx` source files were found in the repository.
3. **Review 2 Historical Drafts in Git:** Early markdown drafts (`Review_2_Report.md`), intermediate Word drafts (`Review_2_Report_Final.docx`), and presentation drafts (`Review_2_ppt.pptx`) existed historically in Git commit `8a6451e`. In commit `755ced2`, they were officially superseded and replaced by `Review_2_Report.pdf` and `Review_2_Presentation.pptx`. The active working tree files are archived here.
4. **Preservation of Documented Limitation:** As verified during Review 3 post-merge testing and documented in Sections 5.2.8 and 8.3 of the final report, default-mode loop refinement has a known limitation involving edge poisoning on dead branches. The quantizer blocks the downstream operand, preserving safety and 100% simulation equivalence across all benchmarks, while the project report maintains rigorous empirical verification rather than an unproven claim of formal universal soundness.
