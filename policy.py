from random import choices


class Policy:

    def __init__(self, belief):
        self.belief_distribution = belief
        self.transition_matrix = self._get_transition_matrix()

    # ACTIONS
    A_START = 0
    A_PREINSTRUCTION = 1
    A_CONCURRENTINSTRUCTIONPOSITIVE = 2
    A_CONCURRENTINSTRUCTIONNEGATIVE = 3
    A_POSTINSTRUCTIONPOSITIVE = 4
    A_POSTINSTRUCTIONNEGATIVE = 5
    A_MANUALMANIPULATION = 6
    A_QUESTIONING = 7
    A_POSITIVEMODELING = 8
    A_NEGATIVEMODELING = 9
    A_FIRSTNAME = 10
    A_HUSTLE = 11
    A_PRAISE = 12
    A_SCOLD = 13
    A_CONSOLE = 14
    A_PREINSTRUCTION_MANUALMANIPULATION = 15
    A_PREINSTRUCTION_QUESTIONING = 16
    A_PREINSTRUCTION_POSITIVEMODELING = 17
    A_PREINSTRUCTION_NEGATIVEMODELING = 18
    A_PREINSTRUCTION_PRAISE = 19
    A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING = 20
    A_CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME = 21
    A_POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION = 22
    A_POSTINSTRUCTIONPOSITIVE_QUESTIONING = 23
    A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING = 24
    A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING = 25
    A_POSTINSTRUCTIONPOSITIVE_FIRSTNAME = 26
    A_POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION = 27
    A_POSTINSTRUCTIONNEGATIVE_QUESTIONING = 28
    A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING = 29
    A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING = 30
    A_POSTINSTRUCTIONNEGATIVE_PRAISE = 31
    A_MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE = 32
    A_MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE = 33
    A_QUESTIONING_NEGATIVEMODELING = 34
    A_QUESTIONING_FIRSTNAME = 35
    A_POSITIVEMODELING_PREINSTRUCTION = 36
    A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE = 37
    A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE = 38
    A_HUSTLE_FIRSTNAME = 39
    A_PRAISE_FIRSTNAME = 40
    A_SCOLD_POSITIVEMODELING = 41
    A_SCOLD_FIRSTNAME = 42
    A_CONSOLE_FIRSTNAME = 43
    A_PREINSTRUCTION_FIRSTNAME = 44
    A_CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE = 45
    A_CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION = 46
    A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING = 47
    A_CONCURRENTINSTRUCTIONPOSITIVE_PRAISE = 48
    A_CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION = 49
    A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING = 50
    A_CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME = 51
    A_POSTINSTRUCTIONNEGATIVE_FIRSTNAME = 52
    A_MANUALMANIPULATION_PREINSTRUCTION = 53
    A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE = 54
    A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE = 55
    A_MANUALMANIPULATION_QUESTIONING = 56
    A_MANUALMANIPULATION_POSITIVEMODELING = 57
    A_MANUALMANIPULATION_FIRSTNAME = 58
    A_MANUALMANIPULATION_HUSTLE = 59
    A_MANUALMANIPULATION_PRAISE = 60
    A_MANUALMANIPULATION_CONSOLE = 61
    A_QUESTIONING_POSITIVEMODELING = 62
    A_POSITIVEMODELING_CONCURRENTINSTRUCTIONNEGATIVE = 63
    A_POSITIVEMODELING_QUESTIONING = 64
    A_POSITIVEMODELLING_HUSTLE = 65
    A_POSITIVEMODELING_PRAISE = 66
    A_END = 67
    A_SILENCE = 68

    # Rewards for all different styles based on Max-Ent IRL.
    rewardsDict = {1: [-1.75616380e-01, 2.97698764e+00, 3.80941213e+00, 1.26260231e+00,
                       2.78465246e+00, 1.52705987e+00, 9.77898413e-02, 3.06854415e+00,
                       7.69818222e-02, -7.85435480e-02, -9.00769590e-03, 3.15102234e-01,
                       4.19660613e+00, 8.74298511e-01, 3.92096766e-01, -3.97058866e-01,
                       -3.12069058e-01, 2.77983452e-01, -3.03278225e-01, -3.46416670e-01,
                       -2.58848328e-01, -1.05863708e-01, -1.30663102e-01, -1.12103019e-01,
                       -2.27442975e-01, -8.18442469e-02, -1.18815092e-01, 3.07194116e-02,
                       3.97163765e-02, -3.74077679e-01, 3.60946472e-01, 3.42765540e-02,
                       9.62164651e-02, -4.33636831e-02, -1.32201700e-01, 2.39797380e-01,
                       -1.30367214e-01, 4.15744950e-03, 4.38573923e-02, -1.23985814e-01,
                       3.49830350e+00, -7.52432170e-02, -8.21662306e-02, -1.77287109e-01,
                       2.55158144e+00],
                   2: [-2.70285329e-01, 2.30472168e+00, 3.30782957e+00, 8.71737247e-01,
                       2.09622599e+00, 1.06666551e+00, -2.69444648e-01, 2.05698837e+00,
                       -1.43943367e-01, 1.41153704e-01, -1.90792824e-01, 1.29191780e+00,
                       4.27684668e+00, 2.93363339e-01, 9.79704531e-01, -8.59228443e-02,
                       -6.40387986e-02, 5.13381493e-01, -2.18108006e-01, -3.90348021e-01,
                       -1.22202538e-01, -3.06345249e-01, -1.07586930e-01, -2.87102782e-01,
                       2.40023326e+00, -3.12477756e-02, -1.55518380e-01, 1.12641118e-02,
                       -2.46649422e-01, 3.70996076e-01, 1.60996220e+00, -6.30889774e-02,
                       -1.34388008e-01, 8.84595742e-02, -2.35640198e-01, -4.49199930e-01,
                       -3.36535355e-03, -4.09436169e-01, -3.03106910e-03, -2.18507811e-01,
                       -1.25935147e-01, -3.70968822e-01, 1.51984816e-01, -1.18297144e-01,
                       1.75594874e+00],
                   3: [-0.43592931, 2.10512153, 4.13021741, 1.43920816, 1.873392, 0.39303976,
                       -0.4294529, 1.56148766, -0.0243192, 0.03627967, -0.17494093, 1.30085817,
                       4.0377656, 0.14982127, 1.31467478, -0.17190704, 0.05194856, 1.10859957,
                       0.42015406, -0.28172486, -0.0616759, -0.18125575, -0.31640082, -0.43671795,
                       2.60710064, 0.04578742, 0.21645476, 0.05072318, -0.36695643, -0.02516701,
                       1.66001829, -0.25904658, -0.17270199, -0.00848569, -0.24022309, -0.25166953,
                       -0.14036979, -0.05068878, -0.13264209, -0.34018902, 0.35765916, -0.06563041,
                       -0.26864788, -0.37170944, 0.41827041],
                   4: [-0.33674984, 3.17125688, 3.48210743, -0.40265294, 2.81615447, 0.94511945,
                       0.2356228, 3.77492525, 0.44743911, 0.39601704, -0.29724195, -0.2587742,
                       4.34313702, 0.0505288, 0.72594047, 0.02339132, -0.22171716, 0.28247877,
                       0.45253625, -0.12646546, -0.30882123, -0.09389028, 0.2963682, -0.28063461,
                       1.69968329, 0.27770837, -0.19628778, 0.24569734, -0.25380533, 0.00661229,
                       1.21850913, -0.35220846, -0.33376541, -0.19280994, 0.04641157, -0.110943,
                       -0.27663098, -0.04175281, -0.12393865, -0.12099647, -0.31737638, -0.33753351,
                       0.04637057, 0.09632173, 1.30239325],
                   5: [-0.20351276, 3.86402855, 3.90726569, 0.154509, 3.94051557, -0.31590969,
                       -0.3773295, 3.63502353, -0.10318342, -0.02839872, 0.08848394, 0.26546061,
                       4.07761811, -0.14680129, 1.50524502, -0.06821302, -0.29899605, 0.46274814,
                       -0.01179475, -0.20980117, -0.24592487, 0.12752541, 0.14404113, 0.07623977,
                       1.69864417, -0.11476335, -0.15763804, -0.19556204, -0.01218348, 0.12760719,
                       -0.17456249, -0.2015564, -0.18814811, 0.06598368, 0.09041736, 0.04828051,
                       -0.04915954, -0.10375017, -0.28730191, 0.0940126, 0.16611978, 0.00963107,
                       -0.15009933, -0.03739598, 3.51587675],
                   6: [-6.01536774e-02, 2.93394999e+00, 3.12550009e+00, -2.72003512e-01,
                       3.40389337e+00, 3.11278291e+00, -3.53148951e-01, 3.54157678e+00,
                       -3.78505386e-01, -2.45719525e-01, -1.96436198e-01, 1.31228607e-01,
                       4.44383069e+00, 2.44709103e-01, 3.79352309e-01, -1.28966427e-01,
                       -5.92297482e-02, -3.20819979e-02, -4.16020949e-01, -1.86513667e-01,
                       9.23772851e-02, 8.09927005e-02, -3.89578158e-01, 2.56448238e-02,
                       3.62277583e-01, -1.47240885e-01, -1.70075078e-01, -4.22560886e-01,
                       -9.07761545e-02, -5.30554636e-02, 4.47444000e-01, 5.13600983e-03,
                       -6.81098278e-02, -3.31984821e-02, -1.27335345e-01, 1.98755483e-02,
                       3.68312766e-03, -3.47736218e-01, -1.27646159e-01, -4.02758118e-01,
                       1.48184918e+00, 5.06697729e-02, -3.51881049e-02, 3.24647593e-01,
                       2.12790873e+00],
                   7: [-4.12906770e-01, 2.72150498e+00, 3.34522329e+00, 1.44406771e+00,
                       1.78206185e+00, 4.94760708e-01, 1.62790641e+00, 2.86505302e+00,
                       1.41934062e-01, -1.22861109e-01, -9.13427981e-02, 6.68962357e-01,
                       3.42955791e+00, -1.68295439e-01, 1.33315316e-01, 1.91617079e-01,
                       9.91010203e-01, -2.96647623e-01, 6.40841293e-01, -2.02467777e-01,
                       3.42140993e-01, 8.48508531e-01, -2.14494479e-01, 4.54787556e-02,
                       -2.36945661e-01, -3.04360040e-01, -8.32819986e-02, -4.60810926e-02,
                       1.39894258e-01, -2.79198363e-01, -1.14758697e-03, -2.21774018e-02,
                       3.53677178e-02, 6.78336453e-01, 3.09549158e+00, 4.45892393e-01,
                       1.18632063e-01, 7.63013169e-03, 9.09231180e-01, -5.43258640e-02,
                       8.60012196e-01, 2.56887436e-01, 1.96972316e+00, 1.72081591e-02,
                       -4.33272329e-01, -3.31936012e-01, 4.76266456e-01, 8.13124750e-02,
                       -2.24455458e-01, -1.40140953e-01, 1.27833962e-01, 6.04016954e-02,
                       1.65136375e+00],
                   8: [-0.12188428, 3.22955711, 4.1295692, 2.16222045, 1.92280854, -0.35071108,
                       3.2312845, 2.76374572, -0.14773734, -0.2356673, 0.07808309, -0.21846304,
                       3.05960916, -0.25828201, -0.09211134, -0.22317667, 0.58522763, -0.27490868,
                       0.05221778, -0.40064802, -0.12828517, -0.19902875, 0.38406938, -0.02820603,
                       -0.28356788, -0.17430809, -0.31469649, -0.14170124, -0.14410204, -0.09880858,
                       -0.3180347, -0.35043184, -0.05801215, -0.40652186, 2.87073197, -0.35705895,
                       -0.04091504, -0.16746471, 1.268586, -0.31357755, -0.10126884, -0.4266439,
                       0.93827644, -0.20033351, -0.22211011, -0.0055, 0.2400364, -0.14924349,
                       -0.18646421, 0.07894781, -0.04644308, -0.12250223, 3.25565748],
                   9: [0.5958506, 6.93916909, 1.57656751, 0.3398724, 0.52835981, 1.02261855,
                       0.84101047, 0.34993765, 0.51650008, 0.46488936, 0.63877423, 0.6495496,
                       1.54738888, 0.24510698, 0.55864072, 0.46044326, 0.72785927, 0.60225415,
                       0.54223885, 0.0919721, 0.4825801, 0.18476498, 0.63476559, 0.6116326,
                       -0.08438245, 0.6107612, 0.53605347, 0.42240693, 0.17182196, 0.50516596,
                       0.22672765, 0.51280237, -0.09164082, 0.12237863, 0.41428134, 0.30846836,
                       0.35469292, 0.52347549, 0.14903929, 0.53975, 0.01308159, 0.64982472,
                       0.32639668, -0.04730835, 0.50891392, 0.1287761, 0.11024732, -0.11158892,
                       0.5727164, 0.10046006, 0.17767167, 0.61875876, 0.25778818],
                   10: [-3.68271315e-01, 2.07511760e+00, 4.30661277e+00, 2.09024504e+00,
                        1.36093798e+00, 5.15161797e-01, 6.70085478e-01, 3.13942039e+00,
                        -2.84241597e-01, 1.00378991e-01, -1.78350197e-01, 1.90532831e+00,
                        3.87347459e+00, 5.40330772e-01, 3.97578936e-01, 1.27463035e-01,
                        2.09241561e+00, 6.04146807e-03, 1.01438166e-01, -1.18783240e-01,
                        9.47478794e-01, 2.11517686e+00, 2.83055726e-01, 9.97474699e-02,
                        -4.48286101e-02, 2.43934533e-02, 2.15936497e-01, -2.70048113e-01,
                        4.35218656e-01, -2.26727081e-01, 7.07879546e-02, 1.11970640e-01,
                        1.53161049e-01, -1.08276851e-01, 7.92044636e-01, -3.10019003e-01,
                        -1.10116722e-01, -2.86511952e-02, 2.99894627e-01, -2.03231763e-01,
                        2.06353448e-01, -4.52985910e-02, 2.93212901e-01, -3.21637651e-02,
                        -3.76345251e-02, 1.67878310e-01, 1.17125684e-02, 1.78832670e-01,
                        2.56562389e-03, 1.41371603e-01, 1.42615829e-01, 7.43720608e-02,
                        1.20403460e+00],
                   11: [-3.67569480e-01, 2.95682885e+00, 3.72995853e+00, 6.51873245e-01,
                        2.69507656e+00, 1.89239714e+00, 1.14377357e+00, 3.05831463e+00,
                        -3.62253782e-01, -1.96332348e-01, 8.23099507e-02, 6.70984606e-01,
                        3.84459028e+00, -9.66149137e-02, 6.86200602e-01, -5.05760332e-02,
                        6.31598722e-01, -7.26002757e-02, 1.24301939e+00, 1.06037634e-02,
                        4.14758447e-03, 1.23108300e+00, -3.12827636e-01, -1.48380882e-01,
                        -2.88929338e-01, -3.02067620e-01, 3.01453875e-02, 4.42965398e-01,
                        1.20482262e+00, 3.73464645e-01, 3.81008758e-02, 5.54759666e-01,
                        9.11750341e-02, 1.48375460e-02, 8.22139252e-01, -1.51816684e-01,
                        -2.15023268e-01, -3.94874295e-01, -2.17403236e-01, -4.10369269e-01,
                        -2.69140065e-01, -1.60211205e-01, 1.96123264e-01, -3.95554243e-01,
                        -1.26960520e-01, 3.61673445e-02, 3.63091915e-04, -2.89801650e-02,
                        7.12061928e-02, -1.66317174e-01, -1.00093562e-01, -3.93209635e-01,
                        2.32703214e+00],
                   12: [-1.47848015e-01, 3.76124991e+00, 2.81834804e+00, 4.88919666e-01,
                        2.61947218e+00, 2.35533351e-01, 7.64435977e-01, 4.31417890e+00,
                        -1.08256268e-01, 3.42467246e-03, -8.16199397e-02, -3.60872133e-01,
                        3.31995174e+00, -1.79082503e-01, -6.31326321e-03, -1.80538321e-01,
                        7.06080636e-01, 3.07599266e-01, -7.84574077e-02, 3.50174752e-02,
                        7.84039178e-01, 5.04697807e-01, -1.75869771e-01, -8.17417130e-02,
                        -1.76321984e-01, -2.51013438e-02, -1.85762575e-01, 1.10438265e-01,
                        5.47577812e-01, 1.15394463e-01, 8.16765644e-02, 1.45462508e-01,
                        1.28380441e-01, -1.65277887e-01, 1.12423850e+00, 3.01407326e-01,
                        -3.15737977e-01, 7.52740725e-02, 2.16846991e-01, -1.18239347e-01,
                        8.00322000e-01, 1.34856250e-01, 4.61224444e-01, -5.14997785e-02,
                        7.55261932e-02, -4.62977527e-02, -2.48617307e-01, 9.42010692e-02,
                        -3.93721734e-01, -2.87195407e-01, -1.44025620e-01, -1.55486447e-01,
                        2.77228134e+00]}

    def sample_action(self, state):
        # Find which style state belongs to.
        style = self._get_style(state)

        # Get random action based on self.transition_matrix probabilities.
        # print(len(self.transition_matrix[style - 1][self._get_action(state)]))
        # print(len(range(68)))
        return choices(range(68), self.transition_matrix[style - 1][self._get_action(state)])[0]
        '''if style < 7:
            action = choices(range(68), self.transition_matrix[style - 1][self._get_action(state)])
            if action == 45:
                action = self.A_END
        else:
            physio_action = choices(range(68), self.transition_matrix[style - 1][self._get_action(state)])
            action = self.physioActionDict[physio_action]

        return action'''

    def sample_observation(self, state, action):
        '''
        Decide whether to move style based on self.belief_distribution and selected action (if it is possible in other
        styles).
        :param state: the current state
        :param action: the chosen behaviour
        :return: the new state we observe based on belief distribution
        '''

        new_style = choices(range(1, 13), self.belief_distribution)[0]

        # Check if action is valid in new_style
        if new_style < 7 and not(43 < action < self.A_END):
            return new_style * 45 + action if action < self.A_END else new_style * 45 + 44
        elif new_style >= 7 and action in self.physioActionDict.values():
            physio_action = next((key for key, value in self.physioActionDict.items() if value == action), None)
            return 270 + ((new_style - 7) * 53) + physio_action

        # If invalid action we don't move, so return original state.
        return state

    def _get_action(self, state):
        # Return the action associated with the given state.
        if state > 269:
            return self.physioActionDict[(state - 270) % 53]

        else:
            if state in [44, 89, 134, 179, 224, 269]:
                return self.A_END
            else:
                return state % 45

    def _get_style(self, state):
        # Return the style associated with the given state.
        if state < 45:
            return 1
        elif state < 90:
            return 2
        elif state < 135:
            return 3
        elif state < 180:
            return 4
        elif state < 225:
            return 5
        elif state < 270:
            return 6
        elif state < 323:
            return 7
        elif state < 376:
            return 8
        elif state < 429:
            return 9
        elif state < 482:
            return 10
        elif state < 535:
            return 11
        else:
            return 12

    def _get_transition_matrix(self):
        tm = [[[0 for x in range(68)] for x in range(68)] for x in range(12)]

        for style in range(1, 13):
            tm[style - 1] = self._get_prob_matrix_from_reward(style)

        return tm

    physioActionDict = {0: A_START,
                        1: A_PREINSTRUCTION,
                        2: A_CONCURRENTINSTRUCTIONPOSITIVE,
                        3: A_CONCURRENTINSTRUCTIONNEGATIVE,
                        4: A_POSTINSTRUCTIONPOSITIVE,
                        5: A_POSTINSTRUCTIONNEGATIVE,
                        6: A_MANUALMANIPULATION,
                        7: A_QUESTIONING,
                        8: A_POSITIVEMODELING,
                        9: A_FIRSTNAME,
                        10: A_HUSTLE,
                        11: A_PRAISE,
                        12: A_SCOLD,
                        13: A_CONSOLE,
                        14: A_PREINSTRUCTION_MANUALMANIPULATION,
                        15: A_PREINSTRUCTION_POSITIVEMODELING,
                        16: A_PREINSTRUCTION_NEGATIVEMODELING,
                        17: A_CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME,
                        18: A_POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION,
                        19: A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING,
                        20: A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING,
                        21: A_POSTINSTRUCTIONPOSITIVE_FIRSTNAME,
                        22: A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                        23: A_MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE,
                        24: A_MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE,
                        25: A_QUESTIONING_NEGATIVEMODELING,
                        26: A_QUESTIONING_FIRSTNAME,
                        27: A_HUSTLE_FIRSTNAME,
                        28: A_PRAISE_FIRSTNAME,
                        29: A_PREINSTRUCTION_FIRSTNAME,
                        30: A_CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE,
                        31: A_CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION,
                        32: A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING,
                        33: A_CONCURRENTINSTRUCTIONPOSITIVE_PRAISE,
                        34: A_CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION,
                        35: A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                        36: A_CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME,
                        37: A_POSTINSTRUCTIONNEGATIVE_FIRSTNAME,
                        38: A_MANUALMANIPULATION_PREINSTRUCTION,
                        39: A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE,
                        40: A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE,
                        41: A_MANUALMANIPULATION_QUESTIONING,
                        42: A_MANUALMANIPULATION_POSITIVEMODELING,
                        43: A_MANUALMANIPULATION_FIRSTNAME,
                        44: A_MANUALMANIPULATION_HUSTLE,
                        45: A_MANUALMANIPULATION_PRAISE,
                        46: A_MANUALMANIPULATION_CONSOLE,
                        47: A_QUESTIONING_POSITIVEMODELING,
                        48: A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE,
                        49: A_POSITIVEMODELING_QUESTIONING,
                        50: A_POSITIVEMODELLING_HUSTLE,
                        51: A_POSITIVEMODELING_PRAISE,
                        52: A_END}

    def _get_prob_matrix_from_reward(self, style):
        irl_rewards = self.rewardsDict[style]
        min_reward = min(irl_rewards)
        non_neg_rewards = [r + min_reward for r in irl_rewards]
        total_rewards = sum(non_neg_rewards)

        prob_matrix = [[0 for x in range(68)] for x in range(68)]
        # print('before')
        # print(len(prob_matrix), len(prob_matrix[0]))
        if style < 7:
            for state in range(44):
                count = 0
                for reward in non_neg_rewards:
                    prob_matrix[state][count] = reward / total_rewards if reward > 0 else 0.00000001
                    count += 1
                prob_matrix[state][67] = non_neg_rewards[44] / total_rewards if non_neg_rewards[44] > 0 else 0.00000001
        else:
            for state in range(53):
                count = 0
                for reward in non_neg_rewards:
                    prob_matrix[self.physioActionDict[state]][count] = reward / total_rewards if reward > 0 else 0.00000001
                    count += 1
        # print('after')
        # print(len(prob_matrix), len(prob_matrix[0]))

        return prob_matrix
