from abc import abstractmethod
from typing import TypeVar, Optional, Callable, Generic

import attr

from doter2.adts.steps import Step, Sequence, Persist, Request, Loop

S = TypeVar("S")
T = TypeVar("T")
STEP = TypeVar("STEP")


@attr.s(auto_attribs=True, frozen=True)
class StepInterpreter(Generic[STEP]):
    step: STEP

    @abstractmethod
    def build_callable(self) -> Callable[[S], T]:
        """Transfroms a step into a function"""
        pass

    def handle_error(self, e: Exception) -> Optional[T]:
        """Override to handle any errors thrown"""
        raise e

    def callable(self) -> Callable[[S], T]:
        c = self.build_callable()

        def run_with_error(s: S) -> T:
            try:
                return c(s)
            except Exception as e:
                return self.handle_error(e)

        return run_with_error


@attr.s(auto_attribs=True, frozen=True)
class SequenceInterpreter(StepInterpreter[Sequence]):
    step: Sequence
    pipeline_interpreter: 'WorkflowInterpreter'

    def build_callable(self) -> Callable[[S], T]:
        validate_seq(self.step)
        interpreters = [self.pipeline_interpreter.build(step) for step in self.step.steps]
        run = lambda x: x
        for interp in interpreters:
            run = compose(run, interp.run)

        def f(s: S) -> T:
            return run(s)

        return f


@attr.s(auto_attribs=True, frozen=True)
class LoopInterpreter(StepInterpreter[Loop]):
    step: Loop
    pipeline_interpreter: 'WorkflowInterpreter'

    def build_callable(self) -> Callable[[S], T]:
        validate_seq(self.step.sequence)
        interpreters = [self.pipeline_interpreter.build(step) for step in self.step.sequence.steps]
        run = lambda x: x
        for interp in interpreters:
            run = compose(run, interp.run)

        return loop(run, self.step.condition, self.step.update)


@attr.s(frozen=True)
class WorkflowInterpreter(Generic[S, T]):
    run: Optional[Callable[[S], T]] = attr.ib(kw_only=True)

    @abstractmethod
    def request_interpreter(self, req: Request[S, T]) -> StepInterpreter[Request[S, T]]:
        raise NotImplementedError

    @abstractmethod
    def persist_interpreter(self, pers: Persist[S]) -> StepInterpreter[Persist[S]]:
        raise NotImplementedError

    def seqeuence_interpreter(self, seq: Sequence[S, T]) -> StepInterpreter[Sequence[S, T]]:
        return SequenceInterpreter(seq, self)

    def loop_interpreter(self, loop: Loop[S, T]) -> StepInterpreter[Loop[S, T]]:
        return LoopInterpreter(loop, self)

    def build(self, step: Step) -> 'WorkflowInterpreter':
        assert isinstance(step, Step)

        if isinstance(step, Request):
            interp = self.request_interpreter(step)
        elif isinstance(step, Persist):
            interp = self.persist_interpreter(step)
        elif isinstance(step, Sequence):
            interp = self.seqeuence_interpreter(step)
        elif isinstance(step, Loop):
            interp = self.loop_interpreter(step)
        else:
            raise Exception("Step not supported by pipeline interpreter: " + str(step))

        return WorkflowInterpreter(run=interp.callable())


def validate_steps(step1: Step, step2: Step) -> None:
    if step1.out_ is not step2.in_:
        raise ValueError(f"Output of step does not match input of next step: [{step1}, {step2}]")


def validate_seq(seq: Sequence) -> None:
    for i in range(len(seq.steps) - 1):
        validate_steps(seq.steps[i], seq.steps[i + 1])


def compose(a, b):
    def f(x):
        return b(a(x))
    return f


def loop(run, condition, update):
    def f(s):
        mutable_state = s
        while condition(mutable_state):
            # super super super dangerous!!
            result = run(mutable_state)
            mutable_state = update((mutable_state, result))
        return mutable_state

    return f
