from enum import Enum
from importlib.resources import path
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from .trust_model import Other, Ego, RootDevice
from .capability_model import InputSystem, RootModel
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from typing import get_origin, get_args, Union, Literal, Any
from types import UnionType
from enum import Enum
import questionary

class ExperienceFormat(Enum):
    UNKNOWN="unknown"
    TIDYBOT2="tidybot2"
    LEROBOTV2="lerobotv2"
    LEROBOTV3="lerobotv3"

class Experience(BaseModel):
    hub_client: str
    experience_format: ExperienceFormat
    trust_structure: RootDevice
    capability_model: RootModel
    input_system: InputSystem

    @classmethod
    def create(cls, prefilled: Optional[dict[str, Any]]=None) -> "Experience":
        return ExperienceWizard.run(cls, **prefilled) if prefilled else ExperienceWizard.run(cls)

    def save_to(self, path: Path | str) -> None:
        if isinstance(path, str):
            path = Path(path)
        if path.suffix != ".json":
            path = path.with_suffix(".json")
        path.write_text(self.model_dump_json(indent=2))

    @staticmethod
    def detect_format(directory: Path) -> ExperienceFormat:
        if not directory.is_dir():
            raise ValueError(f"Directory is not a directory, cannot detect experience format.")
        return ExperienceFormat.UNKNOWN

class ExperienceWizard:
    HELP_TOKEN = "?"
    @classmethod
    def run(cls, model_cls: type[BaseModel], **prefilled) -> BaseModel:
        print("Welcome to the Experience Wizard!")
        print("This wizard will help you create a new experience file.")
        print("Please answer the following questions to the best of your ability.\n")
        return cls.build_model(model_cls, prefilled=prefilled)

 # ---- core recursion -------------------------------------------------

    @classmethod
    def build_model(cls, model_cls: type[BaseModel], prefilled: dict[str, Any] | None = None) -> BaseModel:
        prefilled = prefilled or {}
        # Escape hatch: a model can define its own `ask()` classmethod
        # for bespoke / conditional logic instead of generic reflection.
        if hasattr(model_cls, "ask"):
            return model_cls.ask()

        values = {}
        for name, field in model_cls.model_fields.items():
            if name in prefilled:
                print(f"-- Using provided value for '{name}': {prefilled[name]!r} --")
                values[name] = prefilled[name]
                continue
            values[name] = cls.ask_for_field(name, field.annotation, field)
        return model_cls(**values)

    @classmethod
    def ask_text(cls, prompt: str, name: str, field) -> str:
        while True:
            raw = questionary.text(f"{prompt}  (? for help)").ask()
            if raw == ExperienceWizard.HELP_TOKEN:
                print(f"\n{cls._help_text(field, name)}\n")
                continue
            return raw

    @classmethod
    def ask_select(cls, prompt: str, choices: list[str], name: str, field) -> str:
        while True:
            choice = questionary.select(
                f"{prompt}",
                choices=choices + [questionary.Separator(), "? Help"],
            ).ask()
            if choice == "? Help":
                print(f"\n{cls._help_text(field, name)}\n")
                continue
            return choice

    @classmethod
    def ask_confirm(cls, prompt: str, name: str, field, default: bool = False) -> bool:
        while True:
            raw = questionary.text(f"{prompt} (y/n, ? for help)").ask()
            if raw == ExperienceWizard.HELP_TOKEN:
                print(f"\n{cls._help_text(field, name)}\n")
                continue
            if raw == "":
                return default
            return raw.strip().lower() in ("y", "yes", "true", "1")

    @classmethod
    def _all_subclasses(cls, base: type[BaseModel]) -> list[type[BaseModel]]:
        """Recursively collect every subclass of `base`, deduplicated."""
        seen = set()
        stack = list(base.__subclasses__())
        result = []
        while stack:
            sub = stack.pop()
            if sub not in seen:
                seen.add(sub)
                result.append(sub)
                stack.extend(sub.__subclasses__())
        return result

    @classmethod
    def ask_for_field(cls, name: str, annotation: Any, field) -> Any:
        origin = get_origin(annotation)
        description = field.description or name.replace("_", " ")
        has_default = field.default is not PydanticUndefined
        default_hint = f" [default: {field.default}]" if has_default else ""
        print(f"\n-- Field '{name}' ({description}) --")
        # Optional[...] -> ask whether to include it at all
        if origin in (Union, UnionType) and type(None) in get_args(annotation):
            others = [a for a in get_args(annotation) if a is not type(None)]
            if not cls.ask_confirm(f"Include '{description}'?", name, field, default=False):
                return None
            inner = others[0] if len(others) == 1 else Union[tuple(others)]
            return cls.ask_for_field(name, inner, field)

        # Mixed Union (e.g. str | SomeModel) -> ask how the user wants to answer
        if origin in (Union, UnionType):
            options = get_args(annotation)
            model_options = [o for o in options if isinstance(o, type) and issubclass(o, BaseModel)]
            primitive_options = [o for o in options if o not in model_options]

            if model_options and primitive_options:
                # Build a readable label for each choice: primitives get a friendly
                # name, models get their class name.
                def label(o):
                    return o.__name__ if isinstance(o, type) else str(o)

                choice_labels = [f"Type a value ({label(p)})" for p in primitive_options] + \
                                 [m.__name__ for m in model_options]

                choice = cls.ask_select(
                    f"How would you like to provide '{description}'?",
                    choice_labels,
                    name, field,
                )

                # Dispatch based on which label was picked
                if choice in [m.__name__ for m in model_options]:
                    chosen_cls = next(m for m in model_options if m.__name__ == choice)
                    print(f"-- Filling in '{name}' ({chosen_cls.__name__}) --")
                    return cls.build_model(chosen_cls)
                else:
                    # matched a "Type a value (X)" label -> recurse into that primitive type
                    idx = choice_labels.index(choice)
                    chosen_primitive = primitive_options[idx]
                    return cls.ask_for_field(name, chosen_primitive, field)

            # All-models union (existing behavior)
            if model_options:
                choice = cls.ask_select(
                    f"Which kind of '{description}'?",
                    [m.__name__ for m in model_options],
                    name, field,
                )
                chosen_cls = next(m for m in model_options if m.__name__ == choice)
                print(f"-- Filling in '{name}' ({chosen_cls.__name__}) --")
                return cls.build_model(chosen_cls)

        if origin is dict:
            key_type, value_type = get_args(annotation)
            result: dict[Any, Any] = {}
            print(f"-- Building '{description}' -- add entries one at a time, blank to stop --")
            while True:
                if not cls.ask_confirm(f"Add another entry to '{description}'?", name, field,
                                        default=len(result) == 0):
                    break

                # Build the key: recurse if it's a model, else prompt as a primitive
                if isinstance(key_type, type) and issubclass(key_type, BaseModel):
                    print(f"-- Filling in key ({key_type.__name__}) --")
                    key = cls.build_model(key_type)
                else:
                    raw_key = cls.ask_text(f"Key for this entry:", name, field)
                    if not raw_key:
                        break
                    key = cls._coerce_primitive(raw_key, key_type)

                # Build the value the same way you already do
                if isinstance(value_type, type) and issubclass(value_type, BaseModel):
                    print(f"-- Filling in value ({value_type.__name__}) --")
                    result[key] = cls.build_model(value_type)
                else:
                    result[key] = cls.ask_for_field(f"{name} value", value_type, field)
            return result

        # Nested model -> recurse
        # Base class with subclasses -> let the user pick which concrete type to build
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            subclasses = cls._all_subclasses(annotation)
            if subclasses:
                options = [annotation] + subclasses  # include the base itself as a choice
                choice = cls.ask_select(
                    f"Which kind of '{description}'?",
                    [o.__name__ for o in options],
                    name, field,
                )
                chosen_cls = next(o for o in options if o.__name__ == choice)
                print(f"-- Filling in '{name}' ({chosen_cls.__name__}) --")
                return cls.build_model(chosen_cls)

            # No subclasses -> just a plain nested model
            print(f"-- Filling in '{name}' ({annotation.__name__}) --")
            return cls.build_model(annotation)

        # Enum -> present choices
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            choice = cls.ask_select(
                f"Choose '{description}'{default_hint}:",
                [e.name for e in annotation],
                name, field,
            )
            if choice == "" and has_default:
                return field.default
            return annotation[choice]

        # Literal[...] -> present choices (values, not names)
        if origin is Literal:
            choice = cls.ask_select(
                f"Choose '{description}'{default_hint}:",
                [str(v) for v in get_args(annotation)],
                name, field,
            )
            if choice == "" and has_default:
                return field.default
            for v in get_args(annotation):
                if str(v) == choice:
                    return v

        # list[X] -> repeat prompt until user is done
        if origin in (list,):
            (inner_type,) = get_args(annotation)
            items = []
            print(f"-- Building '{description}' -- add entries one at a time --")
            while True:
                if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                    if not cls.ask_confirm(
                        f"Add another '{inner_type.__name__}'?", name, field,
                        default=len(items) == 0,
                    ):
                        break
                    items.append(cls.build_model(inner_type))
                else:
                    val = cls.ask_text(f"Next value for '{description}' (blank to stop):", name, field)
                    if not val:
                        break
                    items.append(cls._coerce_primitive(val, inner_type))
            return items

        # bool primitive
        if annotation is bool:
            return cls.ask_confirm(f"{description}?{default_hint}", name, field,
                                    default=bool(field.default) if has_default else False)

        # Fallback: primitive text entry
        raw = cls.ask_text(f"Enter '{description}'{default_hint}:", name, field)
        if raw == "" and has_default:
            return field.default
        return cls._coerce_primitive(raw, annotation)

    @staticmethod
    def _coerce_primitive(raw: str, annotation: Any) -> Any:
        if annotation is int:
            return int(raw)
        if annotation is float:
            return float(raw)
        return raw

    @classmethod
    def _help_text(cls, field, name: str) -> str:
        # Prefer an explicit long-form help string if you set one via
        # json_schema_extra={"help": "..."} on the Field, else fall back
        # to the normal description, else a generic placeholder.
        extra = getattr(field, "json_schema_extra", None) or {}
        return extra.get("help") or field.description or f"No additional help available for '{name}'."
