# -*- coding: utf-8 -*-
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

from src.nas import Nas

NAS_GACHA_COST = int(os.environ['NAS_GACHA_COST'])


class TestNas():
    """Function wrapper for executing a NAS command
    In the use of NAS, we often use things like user_id to execute methods.
    If you write it as it is, there will be a lot of arguments,
    so you can group them into classes.
    Arguments are treated as a class variable.

    It's designed based on the user who sent the NAS.
    The information of the destination user is received as an argument.

    Attributes:
        user_id: The user who sent the NAS Slack user id.
        user_name: The user who sent the NAS Slack user name.
        team_id: The user who sent the NAS Slack team id.
    """

    def test_nas_bonus(self, nas_db):
        """Calculate the bonus according to the number you spent last week
        There is a set number of NAS that can be sent in a week. (ex. 30 pieces).

        But for some users, that's not enough.
        In response to that, I implemented a feature where you get an extra NAS depending on the NAS you used last week.
        By default, 20% of the NAS you send will be granted as a bonus.
        """

        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.nas_bonus() == 0

        now = datetime.now()
        nas_now = {
            'tip_user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'receive_user_id': 'test_user_B_id',
            'receive_user_name': 'test_user_B_name',
            'tip_type': 'stamp',
            'tip_user_name': 'test_user_A_name',
            'team_id': 'test_team_id'
        }
        nas_db.put_item(Item=nas_now)
        assert nas_obj.nas_bonus() == 0

        last_week_time = datetime.now() - timedelta(days=7)
        nas_past = {
            'tip_user_id': 'test_user_A_id',
            'time_stamp': Decimal(last_week_time.timestamp()),
            'receive_user_id': 'test_user_B_id',
            'receive_user_name': 'test_user_B_name',
            'tip_type': 'stamp',
            'tip_user_name': 'test_user_A_name',
            'team_id': 'test_team_id'
        }
        nas_db.put_item(Item=nas_past)
        assert nas_obj.nas_bonus() == 1

    def test_sended_nas_num(self, nas_db):
        """Get the number of NAS's you've used this week
        Since the beginning of the week, I tally the number of NAS that I have sent to other users.

        return:
            int : sended nas num
        """
        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.sended_nas_num() == 0

        now = datetime.now()
        nas = {
            'tip_user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'receive_user_id': 'test_user_B_id',
            'receive_user_name': 'test_user_B_name',
            'tip_type': 'stamp',
            'tip_user_name': 'test_user_A_name',
            'team_id': 'test_team_id'
        }
        nas_db.put_item(Item=nas)
        assert nas_obj.sended_nas_num() == 1

    def test_nas_status(self, nas_db):
        """Check the number of NAS you have left
        The number of NAS you can send in a week is determined by the number of NAS you can send in a week.
        By default, you can send 30 pieces a week.
        Check the number of NAS sent by the target user for that week and return the number that can be sent.

        Returns:
            int : remain nas num
        """
        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.nas_status() == 30

        now = datetime.now()
        nas_now = {
            'tip_user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'receive_user_id': 'test_user_B_id',
            'receive_user_name': 'test_user_B_name',
            'tip_type': 'stamp',
            'tip_user_name': 'test_user_A_name',
            'team_id': 'test_team_id'
        }
        nas_db.put_item(Item=nas_now)
        assert nas_obj.nas_status() == 29

        last_week_time = datetime.now() - timedelta(days=7)
        nas_past = {
            'tip_user_id': 'test_user_A_id',
            'time_stamp': Decimal(last_week_time.timestamp()),
            'receive_user_id': 'test_user_B_id',
            'receive_user_name': 'test_user_B_name',
            'tip_type': 'stamp',
            'tip_user_name': 'test_user_A_name',
            'team_id': 'test_team_id'
        }
        nas_db.put_item(Item=nas_past)
        assert nas_obj.nas_status() == 30

    def test_chack_self_portrait(self):
        """Check to see if you're sending yourself an NAS
        Since NAS is a tool for expressing gratitude to others, you can't send it to yourself.
        Check whether the sender's user_id and the destination's user_id are the same.

        Args:
            receive_user_id: The slack user_id of the destination

        Return:
            bool : True if it was sent to yourself.False otherwise
        """

        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.chack_self_portrait('test_user_A_id') is True
        assert nas_obj.chack_self_portrait('test_user_B_id') is False

    def test_check_can_send_nas(self, nas_db):
        """Check to see if user can send the NAS
        Check to see if the target user has more than 0 NAS. And that includes the BONUS portion.

        Return:
            bool : can send is True. can't send is False.
        """

        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.check_can_send_nas() is True

        for i in range(30):
            now = datetime.now()
            nas_now = {
                'tip_user_id': 'test_user_A_id',
                'time_stamp': Decimal(now.timestamp()),
                'receive_user_id': 'test_user_B_id',
                'receive_user_name': 'test_user_B_name',
                'tip_type': 'stamp',
                'tip_user_name': 'test_user_A_name',
                'team_id': 'test_team_id'
            }
            nas_db.put_item(Item=nas_now)

        assert nas_obj.check_can_send_nas() is False

    def test_nas_stamp(self):
        """Sending nas with a Slack stamp
        One of the main ways to send NAS.
        By stamping a specific Slack stamp, you can send a NAS to the stamped user.
        This function only checks the stamp and creates a record.
        Therefore, the return value takes the bool value of whether the stamp was successfully sent or not.
        Also, the stamps are culled out of the settings only in stamp_config.ini so that each can set their own stamp freely.
        Set the target stamp name to the section name. By default, it is set to eggplant.

        Args:
            receive_user_id: The slack user_id of the destination
            receive_user_name : The slack user_name of the destination
            stamp_name : A user sended stamp name

        Return:
            bool : is the stamp sent successfully. success is True. Fail is False.
        """
        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.nas_stamp('test_user_B_id', 'test_user_B_name', 'eggplant') is True

        assert nas_obj.nas_stamp('test_user_B_id', 'test_user_B_name', 'some_stamp') is False

    def test_nas_message(self):
        """Send the NAS with a message.
        Send the NAS with a message.
        A method to send a NAS with a prepackaged message using the nas_message command.
        In this section, we go as far as making a record.
        Sending a message is done by another function.
        Therefore, the return value is the bool value of whether the NAS transmission was successful or not.

        Args:
            receive_user_id: The slack user_id of the destination
            receive_user_name : The slack user_name of the destination

        Return:
            bool : is the nas sent successfully. success is True. Fail is False.
        """
        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.nas_message('test_user_B_id', 'test_user_B_name') is True

        assert nas_obj.nas_message('test_user_A_id', 'test_user_A_name') is False

    def test_check_can_run_gacha(self, nas_gacha_db):
        """Check to see if the gacha is available
        The NAS takes 10 NAS to pull one time.
        Use the NAS you've received so far.
        Gacha costs 10 pieces by default to pull once.
        Calculate that amount and check if you can roll the gacha.
        The first time (when there is no nas_gacha record), it is always possible to draw once.

        Returns:
            bool: available is True. unavailable is False.
        """
        nas_obj_A = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')

        # setup nas_db
        os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'
        dynamoDB = boto3.resource('dynamodb')
        dynamoDB.create_table(
            TableName='NAS',
            AttributeDefinitions=[
                {
                    'AttributeName': 'tip_user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'time_stamp',
                    'AttributeType': 'N'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'tip_user_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'time_stamp',
                    'KeyType': 'RANGE'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 15,
                'WriteCapacityUnits': 5,
            }
        )

        nas_db = dynamoDB.Table('NAS')
        assert nas_obj_A.check_can_run_gacha() is True

        now = datetime.now()
        nas_gacha_item = {
            'user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'has_nas_num': 10,
            'used_nas_num': 0,
            'has_tickets': {}
        }
        nas_gacha_db.put_item(Item=nas_gacha_item)
        assert nas_obj_A.check_can_run_gacha() is False

        now = datetime.now()
        nas_item = {
            'tip_user_id': 'test_user_B_id',
            'time_stamp': Decimal(now.timestamp()),
            'receive_user_id': 'test_user_A_id',
            'receive_user_name': 'test_user_A_name',
            'tip_type': 'stamp',
            'tip_user_name': 'test_user_B_name',
            'team_id': 'test_team_id'
        }
        nas_db.put_item(Item=nas_item)
        assert nas_obj_A.check_can_run_gacha() is False

        for i in range(10):
            now = datetime.now()
            nas_item = {
                'tip_user_id': 'test_user_B_id',
                'time_stamp': Decimal(now.timestamp()),
                'receive_user_id': 'test_user_A_id',
                'receive_user_name': 'test_user_A_name',
                'tip_type': 'stamp',
                'tip_user_name': 'test_user_B_name',
                'team_id': 'test_team_id'
            }
            nas_db.put_item(Item=nas_item)
        assert nas_obj_A.check_can_run_gacha() is True

    def test_nas_gacha_status(self, nas_gacha_db):
        """Calculate the number of times left in the gacha
        At that point, I'll check how many more times I can play the gacha.
        If you haven't turned the gacha once, you can turn it once.

        Return:
            int: Number of times remaining in the gacha
        """
        nas_obj_A = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')

        # setup nas_db
        os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'
        dynamoDB = boto3.resource('dynamodb')
        dynamoDB.create_table(
            TableName='NAS',
            AttributeDefinitions=[
                {
                    'AttributeName': 'tip_user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'time_stamp',
                    'AttributeType': 'N'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'tip_user_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'time_stamp',
                    'KeyType': 'RANGE'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 15,
                'WriteCapacityUnits': 5,
            }
        )

        nas_db = dynamoDB.Table('NAS')
        assert nas_obj_A.nas_gacha_status() == 1

        now = datetime.now()
        nas_gacha_item = {
            'user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'has_nas_num': 0,
            'used_nas_num': 0,
            'has_tickets': {}
        }
        nas_gacha_db.put_item(Item=nas_gacha_item)
        assert nas_obj_A.nas_gacha_status() == 0

        for i in range(10):
            now = datetime.now()
            nas_item = {
                'tip_user_id': 'test_user_B_id',
                'time_stamp': Decimal(now.timestamp()),
                'receive_user_id': 'test_user_A_id',
                'receive_user_name': 'test_user_A_name',
                'tip_type': 'stamp',
                'tip_user_name': 'test_user_B_name',
                'team_id': 'test_team_id'
            }
            nas_db.put_item(Item=nas_item)
        assert nas_obj_A.nas_gacha_status() == 1

    def test_calc_until_next_time_nas_num(self, nas_gacha_db):
        """Calculate how many NAS you need to receive before you roll the NAS gacha
        If you can't roll the gacha, calculate how many NAS you need to receive so you can do it next time.
        If there is no record, you can turn it, so it is set to 0.
        It is assumed that no more than the number received can be used.
        Therefore, there is no case where the difference between the NAS you have and the NAS you used becomes negative.

        Return:
            int: How many NAS you need before you can turn the NAS gacha
        """
        nas_obj_A = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')

        # setup nas_db
        os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'
        dynamoDB = boto3.resource('dynamodb')
        dynamoDB.create_table(
            TableName='NAS',
            AttributeDefinitions=[
                {
                    'AttributeName': 'tip_user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'time_stamp',
                    'AttributeType': 'N'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'tip_user_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'time_stamp',
                    'KeyType': 'RANGE'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 15,
                'WriteCapacityUnits': 5,
            }
        )

        nas_db = dynamoDB.Table('NAS')
        assert nas_obj_A.calc_until_next_time_nas_num() == 0

        now = datetime.now()
        nas_gacha_item = {
            'user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'has_nas_num': 0,
            'used_nas_num': 0,
            'has_tickets': {}
        }
        nas_gacha_db.put_item(Item=nas_gacha_item)
        assert nas_obj_A.calc_until_next_time_nas_num() == NAS_GACHA_COST

        for i in range(NAS_GACHA_COST):
            now = datetime.now()
            nas_item = {
                'tip_user_id': 'test_user_B_id',
                'time_stamp': Decimal(now.timestamp()),
                'receive_user_id': 'test_user_A_id',
                'receive_user_name': 'test_user_A_name',
                'tip_type': 'stamp',
                'tip_user_name': 'test_user_B_name',
                'team_id': 'test_team_id'
            }
            nas_db.put_item(Item=nas_item)
        assert nas_obj_A.calc_until_next_time_nas_num() == 0

    def test_nas_gacha(self, nas_gacha_db):
        """Function to roll Gacha and write the result
        This function is used when the Gacha command is executed.
        Gacha is designed so that the first time you play it, it's free.
        The cost of one turn is 10 NAS received from someone else.
        If you want to roll a gacha, you'll need to get an NAS from someone else.

        Return:
            str : Name of the prize you won
        """
        nas_obj_A = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj_A.nas_gacha() in ['prize_1', 'prize_2', 'prize_3', 'prize_4', 'prize_5', '']

    def test_check_nas_gacha_tickets(self, nas_gacha_db):
        """Check the gacha prizes you've won
        Check the list of giveaways you've won by rolling the Gacha.
        Bring the list of tickets stored in dict format from the latest record.

        Return:
            dict: has tickets dict
        """
        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.check_nas_gacha_tickets() == {}

        now = datetime.now()
        nas_gacha_item = {
            'user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'has_nas_num': 0,
            'used_nas_num': 0,
            'has_tickets': {'prize_1': 1}
        }
        nas_gacha_db.put_item(Item=nas_gacha_item)
        assert nas_obj.check_nas_gacha_tickets() == {'prize_1': 1}

    def test_use_nas_gacha_tickets(self, nas_gacha_db):
        """Consume the tickets you have.
        Consume giveaways won in Gacha.
        False is returned if the item or record does not exist.
        If the remaining number of giveaways in your possession reaches 0, you will be removed from the ticket list

        Args:
            ticket_name : Name of the ticket you want to use

        Return:
            bool : success or fail
        """
        nas_obj = Nas('test_user_A_id', 'test_user_A_name', 'test_team_id')
        assert nas_obj.use_nas_gacha_tickets('prize_1') is False

        now = datetime.now()
        nas_gacha_item = {
            'user_id': 'test_user_A_id',
            'time_stamp': Decimal(now.timestamp()),
            'has_nas_num': 0,
            'used_nas_num': 0,
            'has_tickets': {'prize_1': 1}
        }
        nas_gacha_db.put_item(Item=nas_gacha_item)
        assert nas_obj.use_nas_gacha_tickets('prize_1') is True

        assert nas_obj.use_nas_gacha_tickets('prize_1') is False
