import cv2
import numpy as np
#import matplotlib.pyplot as plt


class CourtReference:
    """
    Court reference model
    """
    def __init__(self):
        self.baseline_top = ((286, 561), (896, 561))
        self.baseline_bottom = ((286, 1902), (896, 1902))
        self.net = ((286, 1171), (896, 1171))
        self.left_court_line = ((286, 561), (286, 1902))
        self.right_court_line = ((896, 561), (896, 1902))
        self.top_inner_line = ((286, 1018), (896, 1018))
        self.bottom_inner_line = ((286, 1445), (896, 1445))
        self.top_middle_line = ((591, 561), (591, 1018))
        self.bottom_middle_line = ((591, 1445), (591, 1902))

        self.court_conf = {1:[*self.baseline_top, *self.baseline_bottom],
                           2:[*self.top_inner_line, *self.bottom_inner_line],
                           3:[*self.baseline_top, *self.top_inner_line],
                           4:[*self.bottom_inner_line, *self.baseline_bottom],
                           5:[*self.baseline_top, *self.bottom_inner_line],
                           6:[*self.top_inner_line, *self.baseline_bottom],
                           7:[self.baseline_top[0], *self.top_middle_line, self.top_inner_line[0]],
                           8:[*self.top_middle_line, self.top_inner_line[1], self.baseline_top[1]],
                           9:[self.bottom_inner_line[0], *self.bottom_middle_line, self.baseline_bottom[0]],
                           10:[*self.bottom_middle_line, self.baseline_bottom[1], self.bottom_inner_line[1]]
                           }
        self.line_width = 1
        self.court_width = 610
        self.court_height = 1340
        self.top_bottom_border = 549
        self.right_left_border = 274
        self.court_total_width = self.court_width + self.right_left_border * 2
        self.court_total_height = self.court_height + self.top_bottom_border * 2

        #self.court = cv2.cvtColor(cv2.imread('court_configurations/court_reference.png'), cv2.COLOR_BGR2GRAY)
        self.build_court_reference()

    def build_court_reference(self):
        """
        Create court reference image using the lines positions
        """
        court = np.zeros((self.court_height + 2 * self.top_bottom_border, self.court_width + 2 * self.right_left_border), dtype=np.uint8)
        cv2.line(court, *self.baseline_top, 1, self.line_width)
        cv2.line(court, *self.baseline_bottom, 1, self.line_width)
        cv2.line(court, *self.net, 1, self.line_width)
        cv2.line(court, *self.top_inner_line, 1, self.line_width)
        cv2.line(court, *self.bottom_inner_line, 1, self.line_width)
        cv2.line(court, *self.left_court_line, 1, self.line_width)
        cv2.line(court, *self.right_court_line, 1, self.line_width)
        cv2.line(court, *self.top_middle_line, 1, self.line_width)
        cv2.line(court, *self.bottom_middle_line, 1, self.line_width)
        court = cv2.dilate(court, np.ones((5, 5), dtype=np.uint8))
        #plt.imsave('court_configurations/court_reference.png', court, cmap='gray')
        self.court = court

    def get_important_lines(self):
        """
        Returns all lines of the court
        """
        lines = [*self.baseline_top, *self.baseline_bottom, *self.net, *self.left_court_line, *self.right_court_line,
                 *self.top_inner_line, *self.bottom_inner_line, *self.top_middle_line, *self.bottom_middle_line]
        return lines

    def save_all_court_configurations(self):
        """
        Create all configurations of 4 points on court reference
        """
        for i, conf in self.court_conf.items():
            c = cv2.cvtColor(255 - self.court, cv2.COLOR_GRAY2BGR)
            for p in conf:
                c = cv2.circle(c, p, 15, (0, 0, 255), 30)
            cv2.imwrite(f'court_configurations/court_conf_{i}.png', c)

    def get_court_mask(self, mask_type=0):
        """
        Get mask of the court
        """
        mask = np.ones_like(self.court)
        if mask_type == 1:  # Bottom half court
            mask[:self.net[0][1] - 1000, :] = 0
        elif mask_type == 2:  # Top half court
            mask[self.net[0][1]:, :] = 0
        elif mask_type == 3: # court without margins
            mask[:self.baseline_top[0][1], :] = 0
            mask[self.baseline_bottom[0][1]:, :] = 0
            mask[:, :self.left_court_line[0][0]] = 0
            mask[:, self.right_court_line[0][0]:] = 0
        return mask


if __name__ == '__main__':
    c = CourtReference()
    c.build_court_reference()
