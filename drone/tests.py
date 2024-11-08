import time

from django.test import TestCase

from common.constants import DRONE_LIMIT
from drone.services import DroneService, LiveDataService
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
        """
        please consider DRONE_LIMIT while adding tests here
        """
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

    def test_create_drone_limit(self):
        for i in range(DRONE_LIMIT):
            drone, error = DroneService.create_drone(self.email, 'test1', 5, 100)
            self.assertIsNone(error)
            self.assertIsNotNone(drone)

        # DRONE_LIMIT + 1
        drone, error = DroneService.create_drone(self.email, 'test1', 5, 100)
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


    def test_update_drone(self):
        original_drone, error = DroneService.create_drone(self.email, 'test1', 5, 100)
        self.assertIsNotNone(original_drone)

        drone, error = DroneService.update_drone('false@mail.com', '', {})
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

        # fix numbers getting saved as name
        # details = {
        #     'name': 5
        # }
        # drone, error = DroneService.update_drone(self.email, original_drone.id, details)
        # self.assertIsNone(drone)
        # self.assertIsNotNone(error)

        details = {
            'name': 'test',
            'flight_time_seconds': -4
        }
        drone, error = DroneService.update_drone(self.email, original_drone.id, details)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

        details = {
            'avg_speed_ms': -5
        }
        drone, error = DroneService.update_drone(self.email, original_drone.id, details)
        self.assertIsNone(drone)
        self.assertIsNotNone(error)

        # check if drone is same
        drone, error = DroneService.get_drone(self.email, original_drone.id)
        self.assertEqual(drone.to_dict(), original_drone.to_dict())


        details = {
            'name': 'test',
            'avg_speed_ms': 10,
            'flight_time_seconds': 200
        }
        drone, error = DroneService.update_drone(self.email, original_drone.id, details)
        self.assertIsNone(error)
        self.assertIsNotNone(drone)

        self.assertEqual(details.get('name'), drone.name)
        self.assertEqual(details.get('avg_speed_ms'), drone.avg_speed_ms)
        self.assertEqual(details.get('flight_time_seconds'), drone.flight_time_seconds)


class TestLiveDataService(TestCase):
    def setUp(self):
        self.email = 'test@mail.com'
        self.password = 'test'

        user, error = UserService.register_user(self.email, self.password)
        self.assertIsNotNone(user)

        drone, error = DroneService.create_drone(
            self.email,
            'test',
            10,
            100
        )
        self.assertIsNotNone(drone)
        self.drone_id = drone.id

    def test_drone_status(self):
        test_data = {
            'drone_id': self.drone_id,
            'latitude': None,
            'longitude': None,
            'status': 'offline'
        }
        live_data = LiveDataService.get_drone_data(self.email, self.drone_id)
        self.assertEqual(test_data, live_data)

        LiveDataService.set_online(self.email, self.drone_id)
        live_data = LiveDataService.get_drone_data(self.email, self.drone_id)
        self.assertEqual(live_data.get('status'), 'online')

        LiveDataService.set_offline(self.email, self.drone_id)
        live_data = LiveDataService.get_drone_data(self.email, self.drone_id)
        self.assertEqual(test_data, live_data)

        LiveDataService.set_online(self.email, self.drone_id)
        live_data = LiveDataService.get_drone_data(self.email, self.drone_id)
        self.assertEqual(live_data.get('status'), 'online')

        time.sleep(11)
        live_data = LiveDataService.get_drone_data(self.email, self.drone_id)
        self.assertEqual(test_data, live_data)

    def test_location(self):
        test_data = {
            'drone_id': self.drone_id,
            'latitude': 10.10,
            'longitude': 20.20,
            'status': 'online'
        }

        is_updated = LiveDataService.set_drone_data(self.email, self.drone_id, test_data)
        self.assertTrue(is_updated)

        live_data = LiveDataService.get_drone_data(self.email, self.drone_id)
        self.assertEqual(test_data, live_data)

        LiveDataService.set_offline(self.email, self.drone_id)

        drone, error = DroneService.get_drone(self.email, self.drone_id)
        self.assertIsNotNone(drone)

        self.assertAlmostEquals(test_data.get('latitude'), float(drone.last_latitude))
        self.assertEqual(test_data.get('longitude'), float(drone.last_longitude))

    def test_multiple_drone_data(self):
        test_data = {
            'drone_id': self.drone_id,
            'latitude': None,
            'longitude': None,
            'status': 'offline'
        }
        data_list = [test_data, test_data, test_data]

        live_data_list = LiveDataService.get_drone_data_by_ids(
            self.email,
            [self.drone_id, self.drone_id, self.drone_id]
        )
        self.assertEqual(data_list, live_data_list)

