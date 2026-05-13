import unittest
from unittest.mock import MagicMock
import main
import Module



class TestDawReeK(unittest.TestCase):

    def setUp(self):
        main.my_cursor = MagicMock()
        main.TEAM_RATING_CACHE = {}
        main.TEAM_DEFAULTS_CACHE = {}
        main.generated_fixtures = [
            [{"home": "Arsenal", "away": "Chelsea", "datetime": "2025-08-01 18:00"}],
            [{"home": "Liverpool", "away": "Man City", "datetime": "2025-08-08 18:00"}],
        ]


    def test_probabilities_sum(self):
        home_win, draw, away_win = Module.match_outcome_probabilities(1.5, 1.2)
        total = home_win + draw + away_win

        self.assertAlmostEqual(total, 1.0, places=2)

    def test_stronger_team_wins(self):

        home_win, draw, away_win = Module.match_outcome_probabilities(3.0, 0.5)
        
        self.assertGreater(home_win, away_win)

        self.assertGreater(home_win, draw)


    def test_predict_goals_is_integer(self):
        home, away,h_win,d,a_win = Module.get_prediction("Arsenal","Liverpool",85,70, 1.5, 0.8, 1.0, 1.2)
        self.assertIsInstance(home, int)
        self.assertIsInstance(away, int)
    
    def test_get_team_rating_default(self):

        main.my_cursor.fetchone.return_value = None
        rating = main.get_team_rating("Unknown Team")
        self.assertEqual(rating, 75.0)

    def test_get_historical_team_defaults_calculation(self):

        main.my_cursor.fetchall.return_value = [(2, 0), (1, 1), (0, 3)]
        points, avg_goals = main.get_historical_team_defaults("Arsenal")

        self.assertEqual(points, 4)
        self.assertAlmostEqual(avg_goals, 1.0)

    def test_get_2025_week_matches(self):
        matches = main.get_2025_week_matches(1)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["home"], "Arsenal")
        self.assertEqual(matches[0]["away"], "Chelsea")
if __name__ == '__main__':
    unittest.main()
