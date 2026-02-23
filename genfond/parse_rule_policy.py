import re
from typing import List, Set
from genfond.rule_policy import Policy, PolicyRule, StateConstraint, Cond, Effect, PolicyType

class PolicyParser:
    def __init__(self):
        self.features = []
        self.rules = []
        self.state_constraints = []
        
    def parse_file(self, filepath: str) -> Policy:
        """Parse a policy file and return a Policy object."""
        with open(filepath, 'r') as f:
            content = f.read()
        return self.parse_string(content)
    
    def parse_string(self, content: str) -> Policy:
        """Parse a policy string and return a Policy object."""
        lines = content.strip().split('\n')
        
        # Parse features
        features_line = next(line for line in lines if line.startswith('features:'))
        self.features = self._parse_features(features_line)
        
        # Find sections
        rules_start = next(i for i, line in enumerate(lines) if line == 'Rules:') + 1
        
        # Check if there are state constraints
        state_constraints_start = None
        for i, line in enumerate(lines):
            if line == 'State Constraints:':
                state_constraints_start = i + 1
                break
        
        # Parse rules
        if state_constraints_start:
            rule_lines = lines[rules_start:state_constraints_start-1]
            constraint_lines = lines[state_constraints_start:]
        else:
            rule_lines = lines[rules_start:]
            constraint_lines = []
        
        # Parse each rule
        self.rules = []
        for line in rule_lines:
            if line.strip() and not line.startswith('{'):
                continue
            if line.strip():
                rule = self._parse_rule(line.strip())
                if rule:
                    self.rules.append(rule)
        
        # Parse state constraints
        self.state_constraints = []
        for line in constraint_lines:
            if line.strip() and line.startswith('{'):
                constraint = self._parse_state_constraint(line.strip())
                if constraint:
                    self.state_constraints.append(constraint)
        
        # Determine policy type
        policy_type = PolicyType.CONSTRAINED if self.state_constraints else PolicyType.EXACT
        
        return Policy(
            features=self.features,
            rules=self.rules,
            state_constraints=set(self.state_constraints),
            type=policy_type
        )
    
    def _parse_features(self, features_line: str) -> List[str]:
        """Parse the features line."""
        # Remove 'features: ' prefix
        features_str = features_line.replace('features: ', '')
        
        # Split by comma, handling nested parentheses
        features = []
        paren_count = 0
        current_feature = ""
        
        for char in features_str:
            if char == ',' and paren_count == 0:
                features.append(current_feature.strip())
                current_feature = ""
            else:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                current_feature += char
        
        # Add the last feature
        if current_feature.strip():
            features.append(current_feature.strip())
        
        return features
    
    def _parse_rule(self, rule_line: str) -> PolicyRule:
        """Parse a single rule line."""
        # Split by ⇒ to get conditions and effects
        parts = rule_line.split('  ⇒  ')
        if len(parts) != 2:
            return None
        
        conditions_str = parts[0].strip('{ }')
        effects_str = parts[1].strip('{ }')
        
        # Parse conditions
        conditions = self._parse_conditions(conditions_str)
        
        # Parse effects
        effects = self._parse_effects(effects_str)
        
        return PolicyRule(conditions, effects)
    
    def _parse_state_constraint(self, constraint_line: str) -> StateConstraint:
        """Parse a single state constraint line."""
        conditions_str = constraint_line.strip('{ }')
        conditions = self._parse_conditions(conditions_str)
        return StateConstraint(conditions)
    
    def _parse_conditions(self, conditions_str: str) -> dict:
        """Parse conditions from a string."""
        conditions = {}
        if not conditions_str.strip():
            return conditions
        
        # Split by ∧ but handle nested parentheses
        condition_parts = self._split_by_conjunction(conditions_str)
        
        for condition in condition_parts:
            condition = condition.strip()
            if not condition:
                continue
                
            # Parse different condition types
            feature, cond_type = self._parse_single_condition(condition)
            if feature:
                conditions[feature] = cond_type
        
        return conditions
    
    def _parse_single_condition(self, condition: str):
        """Parse a single condition and return (feature, Cond)."""
        condition = condition.strip()
        
        # Handle negation
        if condition.startswith('¬'):
            feature = condition[1:].strip()
            return feature, Cond.FALSE
        
        # Handle comparisons
        if ' > 0' in condition:
            feature = condition.replace(' > 0', '').strip()
            return feature, Cond.POSITIVE
        
        if ' = 0' in condition:
            feature = condition.replace(' = 0', '').strip()
            return feature, Cond.ZERO
        
        # Default to TRUE condition
        return condition, Cond.TRUE
    
    def _parse_effects(self, effects_str: str) -> List[List[tuple]]:
        """Parse effects from a string."""
        if not effects_str.strip():
            return [[]]  # Empty effect
        
        # Split by ; for different effect options
        effect_options = effects_str.split(' ; ')
        all_effects = []
        
        for effect_option in effect_options:
            effect_option = effect_option.strip()
            if not effect_option:
                all_effects.append([])
                continue
                
            # Split by ∧ for conjunctive effects
            effect_parts = self._split_by_conjunction(effect_option)
            effects = []
            
            for effect in effect_parts:
                effect = effect.strip()
                if not effect:
                    continue
                    
                feature, effect_type = self._parse_single_effect(effect)
                if feature:
                    effects.append((feature, effect_type))
            
            all_effects.append(effects)
        
        return all_effects
    
    def _parse_single_effect(self, effect: str):
        """Parse a single effect and return (feature, Effect)."""
        effect = effect.strip()
        
        # Handle different effect types
        if effect.startswith('↑'):
            feature = effect[1:].strip()
            return feature, Effect.INCREASE
        
        if effect.startswith('↓'):
            feature = effect[1:].strip()
            return feature, Effect.DECREASE
        
        if effect.startswith('¬'):
            feature = effect[1:].strip()
            return feature, Effect.UNSET
        
        # Default to SET
        return effect, Effect.SET
    
    def _split_by_conjunction(self, text: str) -> List[str]:
        """Split text by ∧ while respecting parentheses."""
        parts = []
        paren_count = 0
        current_part = ""
        
        i = 0
        while i < len(text):
            char = text[i]
            
            if char == '(' :
                paren_count += 1
                current_part += char
            elif char == ')':
                paren_count -= 1
                current_part += char
            elif (char == '∧' or char == '^') and paren_count == 0:
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
            i += 1
        
        # Add the last part
        if current_part.strip():
            parts.append(current_part.strip())
        
        return parts

# Usage example:
def parse_policy_file(filepath: str) -> Policy:
    """Convenience function to parse a policy file."""
    parser = PolicyParser()
    return parser.parse_file(filepath)

# Example usage:
if __name__ == "__main__":
    policy = parse_policy_file("colorballs.policy")
    print(f"Parsed policy with {len(policy.rules)} rules and {len(policy.features)} features")
    print(f"Policy type: {policy.type}")
    print(f"Features: {list(policy.features)}")
    print(f"First rule: {list(policy.rules)[0]}")