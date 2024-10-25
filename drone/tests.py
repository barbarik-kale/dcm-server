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

        drones, message = DroneService.get_drone_list(self.email)
        self.assertIsNone(message)
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

        drone, error = DroneService.create_drone('test@mail.com', 'test', None, 5)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

    def test_get_drone_detail(self):
        drone1, error = DroneService.create_drone(self.email, 'test1', 5, 100)
        self.assertIsNone(error)
        self.assertIsNotNone(drone1)

        drone2, error = DroneService.get_drone(self.email, drone1.id)
        self.assertIsNone(error)
        self.assertIsNotNone(drone2)
        self.assertEqual(drone1.name, drone2.name)
        self.assertEqual(drone1.avg_speed_ms, drone2.avg_speed_ms)
        self.assertEqual(drone1.flight_time_seconds, drone2.flight_time_seconds)

        drone3, error = DroneService.get_drone('false_email@mail.com', drone1.id)
        self.assertIsNone(drone3)
        self.assertIsNotNone(error)

    def test_delete_drone(self):
        drone, error = DroneService.create_drone(self.email, 'test1', 5, 100)
        self.assertIsNotNone(drone)

        drone_id, error = DroneService.delete_drone('false@mail.com', drone.id)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

        drone_id, error = DroneService.delete_drone(self.email, drone.id)
        self.assertIsNone(error)
        self.assertEqual(drone_id, drone.id)

