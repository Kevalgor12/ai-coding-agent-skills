"""
Shared loss-manifest builder.

Per core/skill-specification/adapter-projection.md's Lossiness contract
(L-1 through L-5): every adapter MUST emit a manifest listing each
canonical field it did not represent natively and how it compensated.
This module gives every target adapter one consistent manifest shape
instead of each inventing its own — the same "don't duplicate knowledge"
principle applied to the *reporting* format, not just the projection
logic.
"""

from dataclasses import dataclass, field


@dataclass
class LossEntry:
    field_name: str
    action: str  # "native" | "body" | "drop+note"
    note: str = ""


@dataclass
class LossManifest:
    target: str
    skill_id: str
    entries: list = field(default_factory=list)

    def native(self, field_name: str):
        self.entries.append(LossEntry(field_name, "native"))

    def body(self, field_name: str, note: str = ""):
        self.entries.append(LossEntry(field_name, "body", note))

    def dropped(self, field_name: str, note: str = ""):
        self.entries.append(LossEntry(field_name, "drop+note", note))

    def not_applicable(self, field_name: str, note: str = ""):
        """For fields that are never candidates for projection at all
        (internal taxonomy identity, or content already carried verbatim
        in the body) — distinct from `dropped`, which means "this SHOULD
        have been projectable but wasn't." Still recorded, per L-1's
        literal "every canonical field" requirement — never silently
        absent from the manifest."""
        self.entries.append(LossEntry(field_name, "n/a", note))

    def as_dict(self) -> dict:
        return {
            "target": self.target,
            "skill_id": self.skill_id,
            "entries": [
                {"field": e.field_name, "action": e.action, "note": e.note}
                for e in self.entries
            ],
        }

    def render_markdown(self) -> str:
        lines = [f"# Loss manifest — `{self.skill_id}` → {self.target}", ""]
        lines.append("| Field | Action | Note |")
        lines.append("|---|---|---|")
        for e in self.entries:
            lines.append(f"| `{e.field_name}` | {e.action} | {e.note} |")
        return "\n".join(lines) + "\n"

    def dropped_fields_with_runtime_meaning(self, runtime_meaningful_fields) -> list:
        """L-2 check: any field with runtime meaning that was dropped rather
        than pushed into the body is a lossiness-contract violation."""
        violations = []
        for e in self.entries:
            if e.action == "drop+note" and e.field_name in runtime_meaningful_fields:
                violations.append(e.field_name)
        return violations
