# app/fight_model.py

from app.sparql_client import run_query, run_query_describe
from rdflib import Graph
from random import randint

class PokemonFight:
    def __init__(self, pokemon1_id, pokemon2_id):
        self.pokemon1 = self._get_pokemon_data(pokemon1_id)
        self.pokemon2 = self._get_pokemon_data(pokemon2_id)
        self.current_hp1 = self.pokemon1["hp"]
        self.current_hp2 = self.pokemon2["hp"]
        self.logs = []
        self.winner = None

    def _get_pokemon_data(self, pokemon_id):
        """Fetch Pokémon data from the SPARQL endpoint using DESCRIBE query (N3 format)"""
        query = f"""
        DESCRIBE <http://example.org/pokemon/Pokemon/{pokemon_id}>
        """
        n3_data = run_query_describe(query)
        g = Graph()
        g.parse(data=n3_data, format="n3")

        subject_uri = f"http://example.org/pokemon/Pokemon/{pokemon_id}"
        pokemon_data = {
            "id": pokemon_id,
            "effectiveness": {}
        }

        effectiveness_node = None

        for s, p, o in g:
            if str(s) == subject_uri:
                prop_name = str(p).split("/")[-1]

                if prop_name == "name":
                    pokemon_data["name"] = str(o)
                elif prop_name in ["attack", "defense", "hp", "spAttack", "spDefense", "speed", "totalPoints"]:
                    pokemon_data[prop_name] = int(float(o))
                elif prop_name in ["height", "weight"]:
                    pokemon_data[prop_name] = float(o)
                elif prop_name == "isLegendary":
                    pokemon_data[prop_name] = str(o).lower() == "true"
                elif prop_name in ["primaryType", "secondaryType"]:
                    pokemon_data[prop_name] = str(o).split("/")[-1]
                elif prop_name == "effectiveness":
                    effectiveness_node = str(o)

        # Process effectiveness data
        if effectiveness_node:
            for s2, p2, o2 in g:
                if str(s2) == effectiveness_node and "against" in str(p2):
                    type_name = str(p2).split("/")[-1].replace("against", "").lower()
                    pokemon_data["effectiveness"][type_name] = float(o2)

        return pokemon_data

    def calculate_type_multiplier(self, attacker, defender):
        attacker_type = attacker["primaryType"].lower()
        defender_effectiveness = defender["effectiveness"]
        return defender_effectiveness.get(attacker_type, 1.0)

    def calculate_damage(self, attacker, defender, is_special=False):
        attack_stat = attacker["spAttack"] if is_special else attacker["attack"]
        defense_stat = defender["spDefense"] if is_special else defender["defense"]
        random_factor = randint(85, 100) / 100
        type_multiplier = self.calculate_type_multiplier(attacker, defender)

        base_damage = ((2 * 50 / 5 + 2) * attack_stat * 60 / defense_stat) / 50 + 2
        damage = int(base_damage * random_factor * type_multiplier)
        return max(1, damage)

    def is_battle_over(self):
        if self.current_hp1 <= 0:
            self.winner = self.pokemon2
            return True
        if self.current_hp2 <= 0:
            self.winner = self.pokemon1
            return True
        return False

    def execute_turn(self):
        if self.is_battle_over():
            return False

        first = self.pokemon1 if self.pokemon1["speed"] >= self.pokemon2["speed"] else self.pokemon2
        second = self.pokemon2 if first == self.pokemon1 else self.pokemon1

        self._execute_attack(first, second)
        if self.is_battle_over():
            return True
        self._execute_attack(second, first)
        return self.is_battle_over()

    def _execute_attack(self, attacker, defender):
        is_special = randint(0, 1) == 1
        attack_type = "special" if is_special else "physical"
        damage = self.calculate_damage(attacker, defender, is_special)
        type_multiplier = self.calculate_type_multiplier(attacker, defender)

        if type_multiplier > 1.5:
            effectiveness_msg = "It's super effective!"
        elif type_multiplier < 0.5:
            effectiveness_msg = "It's not very effective..."
        elif type_multiplier == 0:
            effectiveness_msg = "It has no effect..."
            damage = 0
        else:
            effectiveness_msg = ""

        if defender == self.pokemon1:
            self.current_hp1 = max(0, self.current_hp1 - damage)
            hp_remaining = self.current_hp1
        else:
            self.current_hp2 = max(0, self.current_hp2 - damage)
            hp_remaining = self.current_hp2

        self.logs.append(
            f"{attacker['name']} used {attack_type} attack! {effectiveness_msg} "
            f"{damage} damage dealt. {defender['name']} has {hp_remaining} HP remaining."
        )

    def simulate_battle(self):
        while not self.is_battle_over():
            self.execute_turn()

        self.logs.append(f"Battle ended! {self.winner['name']} won the battle!")
        return {
            "winner": self.winner["name"],
            "winner_id": self.winner["id"],
            "logs": self.logs,
            "final_hp": {
                self.pokemon1["name"]: self.current_hp1,
                self.pokemon2["name"]: self.current_hp2
            }
        }

class FightManager:
    @staticmethod
    def battle(pokemon1_id, pokemon2_id):
        return PokemonFight(pokemon1_id, pokemon2_id).simulate_battle()
