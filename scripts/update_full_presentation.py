"""Insert reviewed full-run evidence into the existing course outline."""
from pathlib import Path
import re
from model_labels import readable_text

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "docs/PRESENTATION_OUTLINE.md"
text = path.read_text(encoding="utf-8")
text = text.replace("Numerical result slots remain blank until a complete full experiment is available.",
    "Updated from the complete 258-fit run on 25 October 2026; see [full report](FULL_RESULTS_REPORT.md) and [slide map](FULL_RESULTS_SLIDE_MAP.md). Numerical evidence reconciles, with an execution-source provenance caveat documented in the report.")
text = text.replace("Leave the measured CV result as `[M0 AP, MCC]` until full outputs exist; the point is the hypothesis rather than a presumed weak baseline.",
    "C=1 is selected: mean CV AP is 0.1287; test AP is 0.0714 and MCC 0.0515 at OOF threshold 0.6508. Composition contains some signal but is insufficient here; test prevalence is 0.0434.")
text = text.replace("Fill `[stable pattern]`, `[variable pattern]`, and `[possible explanation]` only from full results.",
    "M1 CV AP is 0.4943 with descriptive SD 0.1032; M4 is 0.5142 with SD 0.0547; M7 is 0.5216 with SD 0.0655. Fold 4 is difficult across neural methods: M1/M4/M7 fold means are 0.3252/0.4153/0.3978. The cause is unresolved.")
text = text.replace("five-question map with brief observed answers, filled after full execution", "five-question map with observed answers below")
text = text.replace("Use only complete full-run evidence. Keep `[result]` placeholders until then.",
    "All inserted numbers use complete full-run evidence. Trace settings and metrics through `FULL_RESULTS_SLIDE_MAP.md`.")
inserts = {
9: "M1 CV AP 0.4943; test AP 0.5408, MCC 0.5495, precision 0.5362 and recall 0.6066 at threshold 0.5125. With 28,801 trainable parameters and no encoder, it remains a strong efficiency reference.",
11: "Selected 8M pooled/single/multi CV AP is 0.3976/0.4868/0.5142; test AP is 0.4764/0.5122/0.5437. Single selects window 3 and 64 filters. Selected multi uses 256 filters per branch and concatenates 1,280 features; label the 64-filter, 320-feature diagram as the default.",
12: "The full run contains 22 configurations: 45 LR CV fits, 195 neural CV fits and 18 final refits, totaling 258. This is a staged search, not a full factorial grid.",
13: "Representative losses decrease while early-stop AP plateaus or fluctuates. Refit epochs M1/M3/M4/M6/M7 are 23/13/16/10/14. Extraction is 9.53 s (8M) versus 13.21 s (35M); mean downstream CV fit times are 10.26 s (M1), 11.50 s (M4), 13.52 s (M7) on the recorded Tesla T4. Timings depend on session state and stopping epoch; they are not deployment latency estimates.",
15: "Window 3 selects AP 0.4868, with only 0.0138 between best and worst window means. Filter AP for 32/64/128/256 is 0.4922/0.5013/0.4985/0.5142, a non-monotonic trend. Weighted/unweighted 64-filter AP is 0.5013/0.4713, while MCC at 0.5 is 0.4225/0.4398. The larger encoder improves multi-window CV/test AP, but pooled and single-window test AP decrease.",
16: "M7 is also the highest CV selection scorer. Test AP M1/M4/M7 is 0.5408/0.5437/0.5758; locked-threshold MCC is 0.5495/0.5512/0.5513. M7 finds 44/61 positives with 52 FP; M1 finds 37 with 32 FP; M4 finds 33 with 22 FP. M7 AP 95% CI is [0.4631, 0.7061]. Exploratory paired M7 minus M1 AP CI is [-0.0444, 0.1151], so superiority is unresolved. Use a complete PR panel here; move the dense all-model confusion grid to the appendix.",
17: "At M7 threshold 0.632288, retained length-35 negative sgh_sequence7831 scores 0.999930 (FP); length-11 neo_sequence56 scores 0.000162 (FN). Do not infer motifs or a padding defect from these examples. State the 61-positive test limit and unverified similarity filtering. The appendix must note that historical and current code hashes differ, so exact execution provenance needs the executed notebook.",
18: "Composition is insufficient; one-hot is a strong efficiency reference; CNN extraction helps pooled 8M features; multi-window gains also add capacity. M7 has the highest observed AP with uncertain differences. End with similarity-aware validation and an external cohort using locked choices, rather than a clinical claim. Assess representation, architecture, threshold, uncertainty and compute together."
}
for number, content in inserts.items():
    marker = f"**Full-run evidence for slide {number}:**"
    if marker in text: continue
    pattern = rf"(^## Slide {number} .+?)(?=^## Slide |^## Appendix)"
    text, count = re.subn(pattern, lambda m: m.group(1).rstrip() + "\n\n" + marker + " " + content + "\n\n", text, count=1, flags=re.M|re.S)
    assert count == 1, number
path.write_text(readable_text(text), encoding="utf-8")
print("Updated presentation outline; preserved 18 titles, timing and existing notes.")
