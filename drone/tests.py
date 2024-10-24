from django.test import TestCase

from drone.services import DroneService
from users.services import UserService


class DroneServiceTest(TestCase):
    email, password = 'test@mail.com', 'test'
    def setUp(self):
        user, error = UserService.register_user(self.email, self.password)
        self.user = user
        self.assertIsNotNone(user)

    def test_get_drone_list(self):
        drone = DroneService.create_drone(self.email, 'kara', 1, 1)
        drone = DroneService.create_drone(self.email, 'kara', 1, 1)
        drone = DroneService.create_drone(self.email, 'kara', 1, 1)
        drone = DroneService.create_drone(self.email, 'kara', 1, 1)

        drones = DroneService.get_drone_list(self.email)
        print(drones)
        self.assertEqual(len(drones), 4)

    def test_create_drone(self):
        drone, error = DroneService.create_drone(self.email, 'test1', 5, 100)
        self.assertIsNone(error)
        self.assertIsNotNone(drone)

        drone, error = DroneService.create_drone(self.email, 'test2', -5, 100)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

        drone, error = DroneService.create_drone(self.email, 'test3', 5, -100)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

        drone, error = DroneService.create_drone(self.email, 'test4', 5, None)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

        drone, error = DroneService.create_drone(self.email, 'test', None, 5)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

