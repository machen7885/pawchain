# Week 2 — exercises

Three exercises, matching Blocks 0, 2 and 3 of the session deck.

---

## Exercise 1 — Assign every failure to exactly one stage (7 min)

Open the twelve worst images from your own capture homework (or, if you have none yet, the
twelve worst you expect once you do). For each, name the **first** stage that should have
stopped it — detect, select, landmark, align, or quality — then name what you would change:
the protocol, the model, or the threshold.

```
stage 1 detect      ___
stage 2 select      ___
stage 3 landmark    ___
stage 4 align       ___
stage 5 quality     ___
protocol, not code  ___

biggest single cause: ________
what I change first:  ________
```

One stage per image. If you cannot choose, the stages are not separated cleanly enough —
which is itself the finding. Expect the last row (protocol, not code) to be the largest; if
it is, you have just discovered why the capture UX matters more than the backbone.

---

## Exercise 2 — Choose the operating point and defend it in one sentence (6 min)

Once you have a real blur sweep from `make eval-capture`, fill this in with your own
numbers (not the illustrative ones below):

```
illustrative sweep, 150 labelled crops

thresh   bad admitted   good rejected
  40         31%             1%
  80         18%             4%
 120          9%            11%
 160          4%            23%
 200          1%            41%
```

```
I set the blur threshold at ____
because ____________________
which costs me ______________
and I prefer that cost because ____________________________.
```

Then answer the follow-up: at your chosen threshold, how many extra capture attempts does
the rejected fraction force, and does enrolment still fit inside the REQ-012 three-minute
budget? Lean strict — a rejected frame costs seconds; an admitted bad template is
permanent.

---

## Exercise 3 — Write the reject message. It is a security decision (4 min)

Write the external, user-facing message for `BLUR`, `POSE_TOO_EXTREME`, and `ILLUMINATION`
— then check it against `ml/capture/types.py::REJECT_MESSAGES`.

**Too vague** — the user gives up: `"Capture failed. Try again."`
**Too specific** — you taught the attacker: `"Blur score 96, need 120. Frames too similar."`
**The target:** tells the user what to *do*, never what the system *measured*. Under eight
words. Names a physical action — move closer, more light, hold steady.

The internal log gets the exact measured value (`Reject.detail`); the person holding the
phone gets the vague-but-actionable version (`Reject.user_message`); the attacker gets
neither.
