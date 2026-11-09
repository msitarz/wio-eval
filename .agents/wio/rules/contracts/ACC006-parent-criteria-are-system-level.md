<!-- wio
code = "ACC006"
name = "parent-criteria-are-system-level"
-->

In a parent, state only the guarantees that the integrated result establishes; a
guarantee one child can establish belongs in that child.

Why: The parent is verified at integration, so a local guarantee there is
checked late and by the wrong stage.
