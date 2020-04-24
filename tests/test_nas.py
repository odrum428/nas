# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from decimal import Decimal

from src.nas import Nas

sys.path.append('../')


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
