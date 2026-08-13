# Skill authoring checklist

- [ ] The name is lowercase kebab-case and matches the directory.
- [ ] The description says both what the skill does and when to use it.
- [ ] The description names adjacent cases that should not trigger it.
- [ ] The body uses imperative instructions and has a clear stop condition.
- [ ] Detailed material is one level below `SKILL.md` and linked at the point of use.
- [ ] No copied text, code, data, or vendor-specific assets lack provenance.
- [ ] Deterministic scripts expose `--help` and have focused tests.
- [ ] At least three positive and two negative routing prompts exist.
- [ ] Behavior cases include observable assertions and at least one edge case.
- [ ] A realistic task or artifact has an isolated baseline/candidate forward test when practical.
- [ ] Grader output, raw artifacts, timing, usage, and protected regressions remain distinguishable.
- [ ] Full validation, plugin checks, and relevant client checks are fresh.
