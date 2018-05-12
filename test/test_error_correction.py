import unittest
from error_correction import error_correction

class TestStringMethods(unittest.TestCase):

    def test_all_valid_sequ(self):
        valid_sequence = [['Orange',  'Black',  'Green'],
                          ['Yellow',  'Black',   'Blue'],
                          [  'Blue',  'Green', 'Orange'],
                          ['Yellow',  'Green',  'Black'],
                          [ 'Black', 'Yellow', 'Orange'],
                          [ 'Green', 'Yellow',   'Blue'],
                          [  'Blue', 'Orange',  'Black'],
                          [ 'Green', 'Orange', 'Yellow'],
                          [ 'Black',   'Blue',  'Green'],
                          ['Orange',   'Blue', 'Yellow']]

        for input_sequ in valid_sequence:
            output_sequ, distance = error_correction(input_sequ)
            self.assertEqual(output_sequ, input_sequ)


    def test_black_yellow_orange_mix(self):
        input_sequences = [['Black', 'Yellow'],
                           ['Black', 'Orange']]
        gt_output = ['Black', 'Yellow', 'Orange']

        for input_sequ in input_sequences:
            output_sequ, distance = error_correction(input_sequ)
            self.assertEqual(output_sequ, gt_output)


    def test_green_orange_yellow_mix(self):
        input_sequences = [['Green', 'Yellow'],
                           ['Green', 'Orange']]
        gt_output = ['Green', 'Orange', 'Yellow']

        for input_sequ in input_sequences:
            output_sequ, distance = error_correction(input_sequ)
            self.assertEqual(output_sequ, gt_output)


    def test_colors_inverted_sequ(self):
        valid_sequence = [['Orange',  'Black',  'Green'],
                          ['Yellow',  'Black',   'Blue'],
                          [  'Blue',  'Green', 'Orange'],
                          ['Yellow',  'Green',  'Black'],
                          [ 'Black', 'Yellow', 'Orange'],
                          [ 'Green', 'Yellow',   'Blue'],
                          [  'Blue', 'Orange',  'Black'],
                          [ 'Green', 'Orange', 'Yellow'],
                          [ 'Black',   'Blue',  'Green'],
                          ['Orange',   'Blue', 'Yellow']]

        for input_sequ in valid_sequence:
            output_sequ, distance = error_correction(list(reversed(input_sequ)))
            self.assertEqual(output_sequ, input_sequ)


    def test_colors_corrections(self):
        input_sequences = [['Orange', 'Black', 'Yellow'],
                           ['Orange',  'Blue',  'Green']]

        gt_output = [['Orange', 'Blue', 'Yellow'],
                     ['Orange', 'Black', 'Green']]

        for input_sequ, gt_sequ in zip(input_sequences, gt_output):
            output_sequ, distance = error_correction(input_sequ)
            self.assertEqual(output_sequ, gt_sequ)


    def test_not_enoug_colors(self):
        input_sequ = ['Orange']
        
        output_sequ, distance = error_correction(input_sequ)
        self.assertEqual(output_sequ, None)



if __name__ == '__main__':
    unittest.main()