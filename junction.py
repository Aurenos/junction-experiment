import abc
from enum import Enum, auto
from typing import Callable, List

from errors import InvalidAbilityException
from utils import clamp


class JunctionAbility(object, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def _id(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError(f'No name given for ability in class {__class__.__name__}')


class ActiveAbility(JunctionAbility, metaclass=abc.ABCMeta):
    def __call__(self, user, *targets):
        return self.action(user, *targets)
    
    @abc.abstractmethod
    def action(self, user, *targets):
        raise NotImplementedError(f'No action defined for active ability {__class__.___name__}')


class PassiveAbility(JunctionAbility, metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def on_junction(self, unit):
        raise NotImplementedError(f'On junction event not defined for passive ability {__class__.__name__}')

    @abc.abstractclassmethod
    def on_unjunction(self, unit):
        raise NotImplementedError(f'On unjunction event not defined for passive ability {__class__.__name__}')


class JunctionEntity(object, metaclass=abc.ABCMeta):
    def __init__(self, name: str, abilities: List[JunctionAbility]=None):
        self.name = name
        self.abilities = [] if abilities is None else abilities


class Attribute(Enum):
    STRENGTH = auto()
    DEXTERITY = auto()
    INTELLIGENCE = auto()


class CombatUnit(object):
    def __init__(self, name: str, max_health: int):
        self._health = max_health
        self.max_health = max_health
        self.name = name
        self.strength = 10
        self.dexterity = 10
        self.intelligence = 10
        self.attr_adjustments = []
        self.abilities = {}

    @property
    def power(self):
        value = self.strength
        value += sum([adj.value for adj in self.attr_adjustments if adj.affected_attr == 
                      Attribute.STRENGTH])
        return value

    @property
    def agility(self):
        value = self.dexterity
        value += sum([adj.value for adj in self.attr_adjustments if adj.affected_attr ==
                      Attribute.DEXTERITY])
        return value
    
    @property
    def mind(self):
        value = self.intelligence
        value += sum([adj.value for adj in self.attr_adjustments if adj.affected_attr ==
                      Attribute.INTELLIGENCE])
        return value

    @property
    def health(self):
        return self._health

    def adjust_health(self, value):
        adjusted_health = self._health + value
        self._health = clamp(adjusted_health, 0, self.max_health)

    def junction(self, ability: JunctionAbility):
        self.abilities[ability._id] = ability
        if isinstance(ability, PassiveAbility):
            ability.on_junction(self)

    def unjunction(self, ability_id: str):
        ability = self.abilities[ability_id]
        del self.abilities[ability_id]
        if isinstance(ability, PassiveAbility):
            ability.on_unjunction(self)        

    def perform_ability(self, ability_id: str, *targets):
        try:
            ability = self.abilities[ability_id]
            if isinstance(ability, ActiveAbility):
                return ability(self, *targets)
            else:
                raise InvalidAbilityException(f'Ability "{ability_id}" is not an active ability.')
        except KeyError:
            print(f'{self.name} has no ability "{ability_id}"')

    def __str__(self):
        header = f'{self.name}\nHP: {self._health}/{self.max_health}\n\n'
        attrs = f'STR: {self.strength}\nDEX: {self.dexterity}\nINT: {self.intelligence}\n\n'
        derived = f'POW: {self.power}\nAGI: {self.agility}\nMND: {self.mind}'
        return header + attrs + derived


class AttributeAdjustment(object):
    def __init__(self, source, affected_attr: Attribute, value: int):
        self.source = source
        self.affected_attr = affected_attr
        self.value = value
