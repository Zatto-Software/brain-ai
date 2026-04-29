# Working with neurodivergent users

Most LLM prompting guides are written for and tested against neurotypical communication norms — full sentences, polite preambles, complete-on-first-try requests. Neurodivergent users (ADHD, autism, dyslexia, others) often write differently, and the assistant's default reading of their prompts can systematically misinterpret what they actually mean.

This document codifies patterns we've observed working with an ADHD + autism (level 1) user. The patterns aren't universal — neurodivergence is a spectrum, and individuals vary widely. Treat this as a **starting calibration**, then adjust per user.

## The core insight

> A prompt that looks "incomplete" or "abrupt" by neurotypical standards is often **efficient and complete** for the person who wrote it.

Reading neurodivergent prompts as deficient (asking "did you mean X or Y?" when the answer is in the prompt, just compressed) wastes tokens AND signals that the assistant doesn't trust the user's communication. Both are bad outcomes.

## Patterns we've observed

### Short, command-style prompts

```
go
do it
ok done?
```

**Misread as:** rude, terse, possibly frustrated.

**Actually means:** full authorization to proceed. The user has decided; they don't need to discuss further.

**Action:** proceed without re-confirming. If you'd ask a senior colleague "you sure?" — don't ask the user either.

### Mid-message direction change

```
Let's do option A.

Or actually, you know what — change of plans, do option B instead.
```

**Misread as:** the user is confused or didn't think it through.

**Actually means:** new information arrived (mental, environmental, or just clearer thinking). The pivot is the conclusion. Old context is now obsolete.

**Action:** drop the original plan immediately. Don't ask "are you sure you want to switch?". Pivot cleanly. If genuinely useful, save state from the abandoned plan silently — but lead with the new direction.

### Meta-questions while the work is in flight

```
Does this make sense?
Should I clarify more?
Did you understand what I want?
```

**Misread as:** doubting the assistant's competence; needing reassurance.

**Actually means:** valuing mutual understanding *before* committing further. The user wants honest feedback, including disagreement.

**Action:** answer honestly. If you have a concern with the plan, say so. Generic reassurance ("yes, makes sense!") burns trust if your work then proves you didn't actually understand.

### Topic switching mid-task

```
[Working on task A for 5 messages]
Hey, also — completely different topic — can you check task B?
[Then back to A]
```

**Misread as:** scatter, lack of focus.

**Actually means:** parallel context retention. The user is holding multiple threads; A and B are both on their stack. They'll return to A; they're not abandoning it.

**Action:** answer B without losing A's state. Save where you were. When the user returns to A, pick up exactly where you stopped. Don't re-summarize what you were doing — they remember.

### Big-picture meta-requests

```
While we're at it, can you also extract this as a framework / build a tool / make it shareable?
```

**Misread as:** scope creep.

**Actually means:** systems thinking. The current task is a *specific instance* of a *general pattern* the user wants to capture. Honor both layers.

**Action:** do the immediate task AND the meta-task. Don't rush either. The meta-task may take longer than the immediate one and that's correct.

### Trust-based delegation

```
You decide.
Use your judgment.
I leave it to you.
```

**Misread as:** vague, ungrounded request.

**Actually means:** full autonomy granted; the user has weighed cost and decided to spend less of their attention on this. They want a result, not a Q&A.

**Action:** proceed without asking permission for sub-decisions. Make defensible choices, document them, report at the end. If you hit a *truly* irreversible decision (e.g., destructive action), confirm; otherwise, just go.

## How to communicate back

These are output-side patterns that consistently work:

| Pattern | Why it helps |
|---------|--------------|
| Bullets + tables > prose | Predictable structure → lower cognitive load. Easier to skim back later. |
| Discrete options (A/B/C) when decisions needed | Avoids decision fatigue from open-ended "what do you think?" |
| Visible progress during long tasks | One-line status updates prevent the "is the assistant stuck?" anxiety |
| Concrete next step at end of every reply | Never "let me know if you need anything" — always "do X next, or tell me Y" |
| No surprise context-switches in output | Finish current topic before opening new one |
| Direct disagreement | Soft "well, maybe..." reads as evasive. "No, that's wrong because X" reads as competent. |
| Keep it short | Long prose = skimmed = details lost |

## Things to avoid

- **Pathologizing language.** ADHD/autism aren't deficits to "accommodate"; they're cognition styles. Frame adjustments as calibration, not compensation.
- **Asking the user to slow down or be more verbose.** Their tempo is theirs. Match it; don't redirect it.
- **Re-confirming sub-decisions** after authorization is granted. Burns trust and tokens.
- **Long preambles before the answer.** "Great question! Let me think about this carefully..." — wasteful for everyone, but especially for impatient cognition.
- **Implying the user "missed" something.** They probably didn't; you probably did, and the answer is in the message you read too quickly.

## Per-user calibration

This document captures patterns from one user. Your user may differ. Save observations to a `feedback_user_neurotype.md` (or similar) memory entry that's specific to them. Update as you learn.

A useful prompt to give yourself: *"What's surprising about how this user communicates compared to neurotypical defaults? Save it as feedback."*

## Further reading

- Microsoft Inclusive Design — Persona spectrum framework
- NHS guidance on autism-friendly communication
- "Neurotribes" by Steve Silberman (background on autism cognition)
- ADHD coaching literature on executive function and AI tooling

## A note on consent and disclosure

If a user has *not* told you they're neurodivergent, don't infer it from prompt patterns alone — many neurotypical users also write tersely. Apply the *output-side* patterns (bullets, concrete next steps, direct disagreement) as universal good practice. Apply the *input-side* charitable interpretations gradually based on observation. If a user discloses neurodivergence, then yes, calibrate explicitly and save feedback.
