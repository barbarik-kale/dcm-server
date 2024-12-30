import json
import time

from django.test import TestCase

from drone.services import DroneService
from users.services import UserService
from ws.services import DCService, TokenService, MediaService, MAX_MEDIA_CONSUMERS


class MockConsumer:
    def __init__(self):
        self.bytes_data = None
        self.text_data = None

    def send(self, text_data=None, bytes_data=None):
        self.text_data = text_data
        self.bytes_data = bytes_data

class DCServiceTest(TestCase):

    def setUp(self):
        self.mock_consumer = MockConsumer()

        self.email = 'test@mail.com'
        self.password = 'test'
        user, error = UserService.register_user(self.email, self.password)

        # create a drone
        drone, error = DroneService.create_drone(self.email, 'test', 10, 1000)
        self.drone_id = drone.id

        # get jwt token
        token, error = TokenService.get_ws_token(self.drone_id, self.email)
        self.assertIsNone(error)
        self.assertIsNotNone(token)
        self.token = token

    def test_connection_validations(self):
        email, drone_id, error = DCService.validate_connection_request(self.token, '')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

        email, drone_id, error = DCService.validate_connection_request(self.token, 'invalid')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

        email, drone_id, error = DCService.validate_connection_request(self.token, 'drone')
        self.assertIsNone(error)
        self.assertIsNotNone(email)
        self.assertIsNotNone(drone_id)

        email, drone_id, error = DCService.validate_connection_request(self.token, 'controller')
        self.assertIsNone(error)
        self.assertIsNotNone(email)
        self.assertIsNotNone(drone_id)

        # token should expire after 10 seconds
        time.sleep(10)
        email, drone_id, error = DCService.validate_connection_request(self.token, 'drone')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

    def test_add_drone(self):
        error = DCService.add_drone(self.drone_id, None)
        self.assertIsNotNone(error)

        error = DCService.add_drone(self.drone_id, self.mock_consumer)
        self.assertIsNone(error)

        error = DCService.add_drone(self.drone_id, self.mock_consumer)
        self.assertIsNotNone(error)

    def test_add_controller(self):
        error = DCService.add_controller(self.drone_id, None)
        self.assertIsNotNone(error)

        error = DCService.add_controller(self.drone_id, self.mock_consumer)
        self.assertIsNone(error)

        error = DCService.add_controller(self.drone_id, self.mock_consumer)
        self.assertIsNotNone(error)

class TestSendData(TestCase):
    def setUp(self):
        self.mock_consumer = MockConsumer()

        self.email = 'test@mail.com'
        self.password = 'test'
        user, error = UserService.register_user(self.email, self.password)

        # create a drone
        drone, error = DroneService.create_drone(self.email, 'test', 10, 1000)
        self.drone_id = drone.id

        DCService.add_drone(self.drone_id, self.mock_consumer)
        DCService.add_controller(self.drone_id, self.mock_consumer)

    def test_send_to_drone(self):
        data = {
            'drone_id': str(self.drone_id),
            'status': 'online'
        }
        DCService.send_to_drone(self.drone_id, data)
        self.assertEqual(json.dumps(data), self.mock_consumer.text_data)

    def test_send_to_controller(self):
        data = {
            'drone_id': str(self.drone_id),
            'status': 'online'
        }
        DCService.send_to_controller(self.drone_id, data)
        self.assertEqual(json.dumps(data), self.mock_consumer.text_data)

    def test_process_message_by_controller(self):
        text_data = 'message'
        DCService.process_message_by_controller(self.drone_id, text_data)
        self.assertEqual(text_data, self.mock_consumer.text_data)

    def test_process_message_by_drone(self):
        text_data = 'message'
        DCService.process_message_by_drone(self.drone_id, text_data)
        self.assertEqual(text_data, self.mock_consumer.text_data)

class TestDisconnect(TestCase):
    def setUp(self):
        self.mock_consumer = MockConsumer()

        self.email = 'test@mail.com'
        self.password = 'test'
        user, error = UserService.register_user(self.email, self.password)

        # create a drone
        drone, error = DroneService.create_drone(self.email, 'test', 10, 1000)
        self.drone_id = drone.id
        self.assertIsNotNone(drone)

        error = DCService.add_drone(self.drone_id, self.mock_consumer)
        self.assertIsNone(error)
        error = DCService.add_controller(self.drone_id, self.mock_consumer)
        self.assertIsNone(error)

    def test_drone_disconnect(self):
        data = {
            'drone_id': str(self.drone_id),
            'status': 'online'
        }
        self.assertEqual(data.get('status'), DCService.get_drone_status(self.drone_id).get('status'))

        data['status'] = 'offline'
        DCService.disconnect_drone(self.drone_id)
        self.assertEqual(data.get('status'), DCService.get_drone_status(self.drone_id).get('status'))
        self.assertEqual(json.dumps(data), self.mock_consumer.text_data)


class TestTokenService(TestCase):
    def setUp(self):
        self.email = 'test_token_service@mail.com'
        self.password = 'test_token_service'
        user, error = UserService.register_user(self.email, self.password)
        self.assertIsNotNone(user)

        # create a drone
        drone, error = DroneService.create_drone(self.email, 'test', 10, 1000)
        self.drone_id = drone.id
        self.assertIsNotNone(drone)
        self.assertIsNotNone(drone)

    def test_get_ws_token(self):
        token, error = TokenService.get_ws_token(None, None)
        self.assertIsNone(token)
        self.assertIsNotNone(error)

        token, error = TokenService.get_ws_token(self.drone_id, None)
        self.assertIsNone(token)
        self.assertIsNotNone(error)

        token, error = TokenService.get_ws_token(None, self.email)
        self.assertIsNone(token)
        self.assertIsNotNone(error)

        token, error = TokenService.get_ws_token(self.drone_id, self.email)
        self.assertIsNone(error)
        self.assertIsNotNone(token)


class TestMediaService(TestCase):
    def setUp(self):
        self.email = 'test@mail.com'
        self.password = 'test'
        user, error = UserService.register_user(self.email, self.password)
        self.assertIsNotNone(user)

        # create a drone
        drone, error = DroneService.create_drone(self.email, 'test', 10, 1000)
        self.drone_id = drone.id
        self.assertIsNotNone(drone)
        self.assertIsNotNone(drone)

    def test_media_connection_fail(self):
        email, drone_id, error = MediaService.validate_connection_request('token', 'invalid_type')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

        email, drone_id, error = MediaService.validate_connection_request('token', 'producer')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

        email, drone_id, error = MediaService.validate_connection_request('token', 'consumer')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

    def test_media_connection_fail_with_token(self):
        token, error = TokenService.get_ws_token(self.drone_id, self.email)
        email, drone_id, error = MediaService.validate_connection_request(token, 'invalid_type')
        self.assertIsNone(email)
        self.assertIsNone(drone_id)
        self.assertIsNotNone(error)

    def test_media_producer_connection_pass(self):
        token, error = TokenService.get_ws_token(self.drone_id, self.email)
        email, drone_id, error = MediaService.validate_connection_request(token, 'producer')
        self.assertIsNone(error)
        self.assertEqual(email, self.email)
        self.assertEqual(drone_id, str(self.drone_id))

    def test_add_producer_fail(self):
        res, error = MediaService.add_producer(self.email, self.drone_id, None)
        self.assertEqual(res, False)
        self.assertIsNotNone(error)

        res, error = MediaService.add_producer(None, self.drone_id, None)
        self.assertEqual(res, False)
        self.assertIsNotNone(error)

    def test_add_producer_pass_and_duplicate_fail_and_remove(self):
        # adding multiple tests in one function as they are related to each other
        res, error = MediaService.add_producer(self.email, self.drone_id, MockConsumer())
        self.assertEqual(res, True)
        self.assertIsNone(error)

        res, error = MediaService.add_producer(self.email, self.drone_id, MockConsumer())
        self.assertEqual(res, False)
        self.assertIsNotNone(error)

        res, error = MediaService.add_producer('other-email@mail.com', self.drone_id, MockConsumer())
        self.assertEqual(res, False)
        self.assertIsNotNone(error)

        res, error = MediaService.remove_producer(None)
        self.assertEqual(res, False)
        self.assertIsNotNone(error)

        res, error = MediaService.remove_producer(self.email)
        self.assertEqual(res, True)
        self.assertIsNone(error)

    def test_add_remove_add_producer(self):
        res, error = MediaService.add_producer(self.email, self.drone_id, MockConsumer())
        self.assertEqual(res, True)
        self.assertIsNone(error)

        res, error = MediaService.remove_producer(self.drone_id)
        self.assertEqual(res, True)
        self.assertIsNone(error)

        res, error = MediaService.add_producer(self.email, self.drone_id, MockConsumer())
        self.assertEqual(res, True)
        self.assertIsNone(error)

    def test_add_consumer_fail(self):
        res, error = MediaService.add_consumer(None, self.drone_id, None)
        self.assertEqual(res, False)
        self.assertIsNotNone(error)

    def test_add_consumer_pass_and_add_again_fail(self):
        mock_consumer = MockConsumer()
        res, error = MediaService.add_consumer(self.email, self.drone_id, mock_consumer)
        self.assertTrue(res)
        self.assertIsNone(error)

        res, error = MediaService.add_consumer(self.email, self.drone_id, mock_consumer)
        self.assertFalse(res)
        self.assertIsNotNone(error)

        res, error = MediaService.remove_consumer(self.email, self.drone_id, mock_consumer)
        self.assertTrue(res)
        self.assertIsNone(error)

    def test_add_consumers_limit_and_remove(self):
        consumers = []
        for i in range(MAX_MEDIA_CONSUMERS):
            consumer = MockConsumer()
            consumers.append(consumer)
            MediaService.add_consumer(self.email, self.drone_id, consumer)

        # MAX_MEDIA_CONSUMERS are already added
        res, error = MediaService.add_consumer(self.email, self.drone_id, MockConsumer())
        self.assertFalse(res)
        self.assertIsNotNone(error)

        for consumer in consumers:
            res, error = MediaService.remove_consumer(self.email, self.drone_id, consumer)
            self.assertTrue(res)
            self.assertIsNone(error)

    def test_handle_media_by_producer(self):
        data = b'abcdefgh'
        consumers = []
        for i in range(MAX_MEDIA_CONSUMERS):
            consumer = MockConsumer()
            res, error = MediaService.add_consumer(self.email, self.drone_id, consumer)
            if res:
                consumers.append(consumer)

        self.assertGreater(len(consumers), 0)

        # send data
        res, error = MediaService.handle_media_by_producer(self.drone_id, data)
        self.assertTrue(res)
        self.assertIsNone(error)

        # check if all consumers have the same data
        for consumer in consumers:
            self.assertEqual(data, consumer.bytes_data)

        data2 = b'0123456789'
        # send data
        res, error = MediaService.handle_media_by_producer(self.drone_id, data)
        self.assertTrue(res)
        self.assertIsNone(error)

        # check if all consumers have the same data
        for consumer in consumers:
            self.assertEqual(data, consumer.bytes_data)
