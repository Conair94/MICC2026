#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
from . import curves as c
from .curves import CurvePair, cycle_to_ladder, ladder_to_cycle
import readline
import sys
from six.moves import range
from six.moves import zip
from six.moves import input

class MiccCore:
    """Headless core logic for MICC, decoupled from terminal I/O."""
    
    def __init__(self):
        self.curve = None
        self.ladder = []
        self.perms = {}

    def set_curve_from_ladder(self, top, bottom):
        """Sets the current curve pair from ladder identifications."""
        if self.is_multicurve(top, bottom):
            self.ladder = [top, bottom]
            self.curve = None
            return False, "Multicurve detected"
        else:
            self.curve = CurvePair(top, bottom)
            self.ladder = [top, bottom]
            return True, "Curve pair set"

    def set_curve_from_cycle(self, cycle_str):
        """Sets the current curve pair from a cycle string."""
        ladder = cycle_to_ladder(cycle_str)
        return self.set_curve_from_ladder(ladder[0], ladder[1])

    def is_multicurve(self, top, bottom):
        if 0 in top or 0 in bottom:
            return c.matrix_is_multicurve([top, bottom])
        else:
            return c.ladder_is_multicurve(top, bottom)

    def get_genus(self):
        if not self.curve: return None
        return self.curve.genus

    def get_boundaries(self):
        if not self.curve: return None
        return self.curve.boundaries

    def get_solution(self):
        if not self.curve: return None
        return self.curve.solution

    def get_distance(self):
        if not self.curve: return None
        return self.curve.distance

    def get_loops(self):
        if not self.curve: return None
        return self.curve.loops

    def get_loop_matrices(self):
        if not self.curve: return None
        return self.curve.loop_matrices

    def get_permutations(self):
        """Returns permutations of the current curve or ladder."""
        source = self.curve.ladder if self.curve else self.ladder
        perms_list = c.test_permutations(source)
        self.perms = {i+1: p for i, p in enumerate(perms_list)}
        return self.perms

    @staticmethod
    def validate_input(top, bottom):
        if len(top) == 0 or len(bottom) == 0: return False
        if len(top) != len(bottom): return False
        
        indices = dict(zip(set(top + bottom), 2 * len(top) * [0]))
        for val in top:
            indices[val] += 1
        for val in bottom:
            indices[val] += 1
        
        return all(x == 2 for x in indices.values())

class CLI:
    """Terminal-based UI for MICC."""

    def __init__(self, core=None):
        self.core = core or MiccCore()
        self.commands = {
            'genus': self.ui_get_genus,
            'faces': self.ui_get_faces,
            'perm': self.ui_get_perms,
            'distance': self.ui_get_distance,
            'curves': self.ui_get_curves,
            'matrix': self.ui_get_matrix,
            'help': self.ui_get_help,
            'change': self.ui_change,
            'exit': self.quit,
            'quit': self.quit,
            'bye': self.quit
        }

    def correct_input(self, ladder):
        ladder = [s.strip() for s in ladder if s.strip()]
        return [int(num) for num in ladder]

    def ui_get_genus(self):
        genus = self.core.get_genus()
        if genus is not None:
            print("Genus: ", genus)
        else:
            print("No curve loaded.")
        return False

    def ui_get_faces(self):
        bdy = self.core.get_boundaries()
        sol = self.core.get_solution()
        if bdy and self.core.curve:
            print('%s faces with %s bigons' % tuple(bdy))
            print('Vector solution: ', sol)
            for face in self.core.curve.edges[0]:
                print(tuple(face[1]))
        else:
            print("No curve loaded.")
        return False

    def ui_get_distance(self):
        dist = self.core.get_distance()
        if dist is not None:
            print('Distance: ', dist)
        else:
            print("No curve loaded.")
        return False

    def ui_get_perms(self):
        perms = self.core.get_permutations()
        if not perms:
            print("No permutations found or no ladder loaded.")
            return False
        for index, perm in perms.items():
            print('\nCurve %d Distance: %s' % (index, perm.distance))
            print(perm.ladder[0])
            print(perm.ladder[1])
        return False

    def ui_get_curves(self):
        if not self.core.curve:
            print("No curve loaded.")
            return False
            
        view = input("Would you like to view the vertex paths, the corresponding matrices, or both? ")
        loops = self.core.get_loops()
        matrices = self.core.get_loop_matrices()
        
        for itr in range(len(loops)):
            loop = loops[itr]
            matrix = list(matrices.values())[itr]
            Genus = c.genus(matrix)

            if view in ['paths', 'both']:
                print('Path', loop)
            if view in ['matrices', 'both']:
                print('Matrix: \n', matrix[0])
            print('Curve genus: ', Genus, '\n')
        return False

    def ui_get_matrix(self):
        if self.core.curve:
            print(self.core.curve.matrix)
        else:
            print("No curve loaded.")
        return False

    def ui_get_help(self):
        print(''' Welcome to curvePair.
        \n With this program, by supplying a pair of curves you can determine:
        \n 1. The genus of the surface on which the curves fill (say 'genus')
        \n 2. The number of boundary components in the complement of the curve pair on such a surface , and the vector solution (say 'faces')
        \n 3. The distance between the two curves in the curve complex, up to distance four (say 'distance')
        \n 4. The curves in the complement of the non-reference curve that were used for calculating distance (say 'curves')
        \n 5. To work with a different curve pair, say 'change'
        \n 6. To see the matrix associated with the curve, say 'matrix'
        \n 7. If a ladder is entered, can see the different curves that result from permutations of the identifications in that ladder (say perm)
        \n
        \n ---------------begin curve entry help -------------
        \n Instructions for entering curves: Using an orientation and reference
        \ncurve of your choice, please number the intersections of the two curves
        \n(starting from 1). Then trace out the non-referential curve, identifying
        \nwhich of the intersections are connected. Keep track of whether each
        \nconnection is above or below the reference curve. The program will ask
        \nfor a comma-separated list of these connections, starting from the
        \nones which come from above and then the ones which come from below.
        \nFor example: if the first vertex (1) is connected to the fifth (5) from
        \nabove, then the first number you will enter is a 5, and so on.

        \nAlternatively, you can number the identifications(edges) from 1 to
        \n the number of edges and enter those that are on the top
        \n and those that are on the bottom.
        \n ------------------ end help ----------------------

        \n Note: say 'done' to exit
        ''')
        return False

    def ui_change(self):
        cycle_or_ladder = input('Would you like to describe curves as a ladder or a cycle?\n (Type \'cycle\' or \'ladder\'): ')
        
        valid = False
        while not valid:
            if cycle_or_ladder == 'ladder':
                top_str = input('Input top identifications: ')
                if top_str.lower() in ['exit', 'quit']: sys.exit()
                top = self.correct_input(top_str.split(','))
                
                bottom_str = input('Input bottom identifications: ')
                bottom = self.correct_input(bottom_str.split(','))
                
                if not self.core.validate_input(top, bottom):
                    print("There seems to be an error in your entry. Please try again.")
                    continue
                
                print('Input (as a cycle):', ladder_to_cycle(top, bottom))
                print('Input (as a ladder):\n', top, '\n', bottom)
                
                success, msg = self.core.set_curve_from_ladder(top, bottom)
                valid = True
                
            elif cycle_or_ladder == 'cycle':
                cycle = input('Input cycle: ')
                print('Input (as a cycle):', cycle)
                ladder = cycle_to_ladder(cycle)
                print('Input (as a ladder):\n', ladder[0], '\n', ladder[1])
                
                if not self.core.validate_input(ladder[0], ladder[1]):
                    print("There seems to be an error in your entry. Please try again.")
                    continue
                    
                success, msg = self.core.set_curve_from_cycle(cycle)
                valid = True
            else:
                cycle_or_ladder = input('Please type \'cycle\' or \'ladder\': ')

        if not success: # Multicurve
            ans = input('Would you like to shear this multicurve? ')
            if ans.lower() == 'yes':
                self.ui_get_perms()
                self.ui_change()
            else:
                print('Better luck next time.')
                sys.exit()
        else:
            print('Note: if you permute a curve with \'perm\', the sheared curves will be lost.')
        
        return False

    def process_input(self):
        while True:
            cmd = input("What would you like to calculate? ").strip().lower()
            if cmd in ['done', 'exit', 'quit']:
                return True
            if cmd in self.commands:
                return self.commands[cmd]()
            else:
                input("Sorry, I didn't quite catch that. Press enter and try again. ")

    def quit(self):
        sys.exit()

    def run(self):
        self.ui_get_help()
        self.ui_change()
        exit_status = False
        while not exit_status:
            exit_status = self.process_input()

if __name__ == "__main__":
    CLI().run()
