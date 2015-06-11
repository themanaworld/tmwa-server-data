# To-do
- [ ] finish the missing spells and push them so they can be tested

---
---
to see other things that needs to be done do a grep for `TODO`, `FIXME` in this folder.
To see a list of things that needs further thoughts do a grep for `XXX`.

---
---

- [ ] check the new builtins and make sure they work as intended
 - [ ] `puppet`
    - [ ] check what happens when making a puppet whose name already exist (maybe it replaces?)
 - [ ] `destroy`
 - [ ] `registercmd`
    - [ ] check what happens when registering a command that was already registered
 - [ ] `target`
 - [ ] `get`
 - [ ] the new `set`
 - [ ] `min`
 - [ ] `max`
 - [ ] `pow`
 - [ ] `sqrt`
 - [ ] `cbrt`
 - [ ] `elttype`
 - [ ] `eltlvl`
 - [ ] `injure`
 - [ ] `elif`
 - [ ] `else`
 - [ ] `getnpcid`
 - [ ] `overrideattack`
 - [ ] `summon`
 - [ ] `addnpctimer`
 - [ ] `explode`
 - [ ] `foreach`
 - [ ] modified `areatimer`
 - [ ] `aggravate`
 - [ ] `getdir`
 - [ ] `distance`
 - [ ] `if_then_else`

---
- [ ] test the spells
 - [ ] test with no target
 - [ ] test with a npc target
    - [ ] random npc not part of any quest
    - [ ] injured mouboo
       - [ ] also test on a **player** with the name `Mouboo` or `mouboo`
    - [ ] druid tree
 - [ ] test with a mob target
    - [ ] mob with clear path (walkable)
    - [ ] mob with no clear path (unwalkable, blocked by collision)
    - [ ] mob out of attack range
 - [ ] test with a player target
    - [ ] both the caster and the target have pvp disabled
    - [ ] both the caster and the target have pvp enabled
    - [ ] the caster has pvp enabled and the target has pvp disabled
    - [ ] the caster has pvp disabled and the target has pvp enabled
 - [ ] test with the spouse as target

---
- [ ] Once everything is done, remove this file
