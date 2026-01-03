from __future__ import annotations
from typing import Callable, List, Tuple, TypeAlias
from dataclasses import dataclass

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok


NestedFloatList: TypeAlias = list["float | Tuple[NestedFloatList, float]"]


@dataclass(slots=True)
class Component:
    """
    Base class for components in a chemical formula.

    Attributes
    ----------
    count : float
        The subscript count for the component.
    """

    count: float


@dataclass(slots=True)
class Element(Component):
    """
    A chemical element in a formula.

    Attributes
    ----------
    symbol : str
        The chemical symbol of the element.
    """

    symbol: str


@dataclass(slots=True)
class Group(Component):
    """
    A group of components in a chemical formula.

    Attributes
    ----------
    components : List[Component]
        The list of components (elements and groups) in the group.
    """

    components: List[Component]


class Formula(list[Component]):
    """
    A chemical formula consisting of elements and groups.

    Methods
    -------
    from_string(source: str) -> Result[Formula, Exception]
        Parse a chemical formula from a string.
    elements() -> List[str]
        Get a list of unique element symbols in the formula.
    """

    @classmethod
    def from_string(cls, source: str) -> Result[Formula, Exception]:
        """
        Initialize a chemical formula from a string.

        Parameters
        ----------
        source : str
            The source string representing the chemical formula.

        Returns
        -------
        Result[Formula, Exception]
            - Success(Formula) if parsing is successful.
            - Failure(Exception) if parsing fails.
        """
        res = parse_formula(source)
        if ok(res):
            components = res.unwrap()
            return Success(cls(components))
        else:
            return Failure(res.failure())

    def elements(self) -> List[str]:
        """
        Get a list of unique element symbols in the formula.

        Returns
        -------
        List[str]
            A list (set) of unique element symbols present in the formula.
        """
        elems = []
        for comp in self:
            if isinstance(comp, Element):
                elems.append(comp.symbol)
            elif isinstance(comp, Group):
                elems.extend(Formula(comp.components).elements())
        return list(set(elems))

    def counts(self) -> NestedFloatList:
        """
        Get the counts (subscripts) of all components in the formula.

        Returns
        -------
        NestedFloatList
            A list of counts, where each count is either a float (for elements)
            or a tuple of (NestedFloatList, float) for groups.
        """
        counts: NestedFloatList = []
        for comp in self:
            if isinstance(comp, Element):
                counts.append(comp.count)
            elif isinstance(comp, Group):
                counts.append((Formula(comp.components).counts(), comp.count))
        return counts

    def is_chem_valid(self) -> bool:
        """
        Check if the formula is chemically valid.

        Returns
        -------
        bool
            True if the formula is chemically valid, False otherwise.

        Notes
        -----
        This function only checks the validity of subscripts and group structure, given that the normal parsing allows for fractional subscripts to support mixed compounds.

        A formula is considered chemically valid if:

        - All elements have subscripts that are positive integers.
        - All groups are chemically valid recursively.
        """
        for comp in self:
            if isinstance(comp, Element):
                if comp.count % 1 != 0.0 or comp.count <= 0:
                    return False
            elif isinstance(comp, Group):
                if not Formula(comp.components).is_chem_valid():
                    return False
        return True


def parse_formula(source: str) -> Result[List[Component], Exception]:
    """
    Parse the entire source string into a list of components.

    Parameters
    ----------
    source : str
        The source string to parse.

    Returns
    -------
    Result[List[Component], Exception]
        - Success(components) if parsing is successful.
        - Failure(Exception) if parsing fails.
    """
    index = 0
    if ok(res := parse_section(source, index)):
        components, next_index = res.unwrap()
        if next_index != len(source):
            return Failure(
                ValueError(
                    f"Unexpected characters at end of formula: {source[next_index:]} @index {next_index}"
                )
            )
        return Success(components)
    else:
        return Failure(res.failure())


def parse_section(
    source: str, start: int
) -> Result[Tuple[List[Component], int], Exception]:
    """
    Parse a section of the source string starting at the given index until a closing parenthesis or the end of the string.

    Parameters
    ----------
    source : str
        The source string to parse.
    start : int
        The starting index in the source string.

    Returns
    -------
    Result[Tuple[List[Component], int], Exception]
        - Success((components, last_index)) if parsing is successful.
        - Failure(Exception) if parsing fails.
    """
    index = start
    components: List[Component] = []

    while index < len(source) and source[index] != ")":
        char = source[index]
        func: Callable
        if char.isalpha():
            func = extract_component
        elif char == "(":
            func = extract_group
        else:
            return Failure(ValueError(f"Unexpected character: {char} @index {index}"))

        if ok(res := func(source, index)):
            component, next_index = res.unwrap()
            components.append(component)
            if next_index == index:
                return Failure(
                    ValueError(f"No progress made during parsing @index {index}")
                )
            index = next_index
        else:
            return Failure(res.failure())

    return Success((components, index))


def extract_group(source: str, start: int) -> Result[Tuple[Group, int], Exception]:
    """
    Extract a group component along with an optional subscript from the source string starting at the given index.

    Parameters
    ----------
    source : str
        The source string to extract the group from.
    start : int
        The starting index in the source string.

    Returns
    -------
    Result[Tuple[Group, int], Exception]
        - Success((Group, last_index)) if a valid group is found.
        - Failure(Exception) if no valid group is found.

    Notes
    -----
    A group is defined as a sequence of components enclosed in parentheses,
    followed by an optional subscript indicating the count of the group.
    Nested groups are supported.
    """
    if source[start] != "(":
        return Failure(ValueError(f"Group must start with '(' @index {start}"))
    index = start + 1

    if ok(section_result := parse_section(source, index)):
        comps, index = section_result.unwrap()
    else:
        return Failure(section_result.failure())

    if index >= len(source) or source[index] != ")":
        return Failure(ValueError(f"Unmatched '(' in group @index {index}"))
    index += 1  # Skip ')'

    count: float = 1.0
    if ok(num_result := extract_number(source, index)):
        count, index = num_result.unwrap()
    elif not isinstance(num_result.failure(), IndexError):
        return Failure(num_result.failure())
    if count <= 0:
        return Failure(ValueError(f"Subscript must be > 0 @index {index}"))

    return Success((Group(components=comps, count=count), index))


def extract_component(
    source: str, start: int
) -> Result[Tuple[Element, int], Exception]:
    """
    Extract an element component along with an optional subscript from the source string starting at the given index.

    Parameters
    ----------
    source : str
        The source string to extract the element from.
    start : int
        The starting index in the source string.

    Returns
    -------
    Result[Tuple[Element, int], Exception]
        - Success((Element, last_index)) if a valid element is found.
        - Failure(Exception) if no valid element is found.
    """
    if not source[start].isupper():
        return Failure(
            ValueError(
                f"Element symbol must start with an uppercase letter @index {start}."
            )
        )
    index = start + 1
    while True:
        if index >= len(source):
            break
        char = source[index]
        if not char.islower():
            break
        index += 1
    symbol = source[start:index]
    count: float = 1.0
    if ok(num_result := extract_number(source, index)):
        count, index = num_result.unwrap()
    elif not isinstance(num_result.failure(), IndexError):
        return Failure(num_result.failure())
    if count <= 0:
        return Failure(ValueError(f"Subscript must be > 0 @index {index}"))

    return Success((Element(symbol=symbol, count=count), index))


def extract_number(source: str, start: int) -> Result[Tuple[float, int], Exception]:
    """
    Extract a (floating-point) number from the source string starting at the given index.

    Parameters
    ----------
    source : str
        The source string to extract the number from.
    start : int
        The starting index in the source string.

    Returns
    -------
    Result[Tuple[float, int], Exception]
        - Success((number, last_index)) if a valid number is found.
        - Failure(Exception) if no valid number is found.

    Notes
    -----
    A valid number consists of digits and at most one decimal point.
    Thus both integers and floating-point numbers are supported.
    """
    index = start
    decimal_found = False
    while True:
        if index >= len(source):
            break
        char = source[index]
        if not char.isdigit() and char != ".":
            break
        if char == ".":
            if decimal_found:
                return Failure(
                    ValueError(
                        f'Invalid number format: multiple decimals found: "{source[start:index+1]}" @index {index}'
                    )
                )
            decimal_found = True
        index += 1
    if index == start:
        return Failure(IndexError(f"Expected a number @index {start}"))
    try:
        number = float(source[start:index])
        return Success((number, index))
    except ValueError as e:
        return Failure(e)
