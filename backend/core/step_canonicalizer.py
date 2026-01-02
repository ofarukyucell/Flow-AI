from backend.models.schemas import StepProof

def canonicalize_step(step: StepProof) -> StepProof:
    action = (step.action or "").strip()
    step.action = action

    if ":" in action:
        verb, obj = [x.strip() for x in action.split(":",1)]

        if verb == obj:
            step.action = verb
            return step
        
        if verb in ["bas","tıkla","tikla"]:
            step.action = obj
            return step
        
        if verb == "gir":
            step.action = f"{obj} gir"
            return step
    return step