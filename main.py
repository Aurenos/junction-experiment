import random
from typing import List

from junction import ActiveAbility, PassiveAbility, CombatUnit, Attribute, AttributeAdjustment


class HealAbility(ActiveAbility):
    @property
    def _id(self):
        return 'heal'

    @property
    def name(self):
        return 'Heal'
    
    def action(self, user, *targets: List[CombatUnit]):
        healed = random.randint(5, 10)
        target = targets[0]
        target.adjust_health(healed)
        print(f'{user.name} casts {self.name} on {target.name}!')
        print(f'{target.name} heals {healed} health!')

class AttackAbility(ActiveAbility):
    @property
    def _id(self):
        return 'attack'

    @property
    def name(self):
        return 'Attack'

    def action(self, user, *targets: List[CombatUnit]):
        damage = (random.randint(1, 10) + user.power) // 2
        target = targets[0]
        target.adjust_health(-damage)
        print(f'{user.name} attacks {target.name}!')
        print(f'{target.name} takes {damage} damage!')


class StrengthUpAbility(PassiveAbility):
    @property
    def _id(self):
        return 'str-up'

    @property
    def name(self):
        return 'Strength Up'

    def on_junction(self, unit: CombatUnit):
        str_up = AttributeAdjustment(self._id, Attribute.STRENGTH, 10)
        unit.attr_adjustments.append(str_up)
    
    def on_unjunction(self, unit: CombatUnit):
        unit.attr_adjustments = [adj for adj in unit.attr_adjustments if adj.source != self._id]


class Unit(CombatUnit):
    def __init__(self, name: str, max_health: int):
        super(__class__, self).__init__(name, max_health)


if __name__ == '__main__':
    unit1 = CombatUnit('Arthur', 20)
    unit2 = CombatUnit('Zora', 20)
    attack = AttackAbility()
    str_up = StrengthUpAbility()
    unit1.junction(attack)

    unit1.perform_ability('attack', unit2)
    unit1.junction(str_up)
    unit1.perform_ability('attack', unit2)
