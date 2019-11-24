#!/usr/bin/env python

"""tasksscraper.trello: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

from trello import TrelloClient
from loguru import logger
from typing import List
# import keyring


def find_my_id(input_client, input_name):
    all_boards = input_client.list_boards()
    for b, board in enumerate(all_boards):
        all_cards = board.all_cards()
        for c, card in enumerate(all_cards):
            logger.debug(f'processing board {b}/{len(all_boards)}, card {c}/{len(all_cards)}')
            for member_id in card.member_ids:
                if input_name in input_client.get_member(member_id).full_name:
                    logger.info(f'found {input_name} as id {member_id}')
                    return member_id


def get_all_board_ids(input_client, input_tasks):
    all_ids = set()
    for t in input_tasks:
        all_ids.add(t['idBoard'])
    return {i: input_client.get_board(i).name for i in all_ids}


def add_project(input_my_tasks, board_ids):
    output_tasks = []
    for t in input_my_tasks:
        current_item = t
        current_item['project'] = board_ids[t['idBoard']]
        output_tasks.append(current_item)
    return output_tasks


def get_trello_tasks(api_key: str, token: str, token_secret: str, my_name: str) -> List:
    """Query Trello for tickets

    Args:
        my_name:
        api_key:
        token:
        token_secret:

    Returns:
        List of tasks

    """

    client = TrelloClient(
        api_key=api_key,
        api_secret=None,
        token=token,
        token_secret=token_secret
    )

    logger.info('fetching Trello tickets')

    my_id = find_my_id(client, my_name)
    my_cards = client.get_member(my_id).fetch_cards()
    board_ids = get_all_board_ids(client, my_cards)
    all_tickets = add_project(my_cards, board_ids)

    logger.info(f'complete fetching {len(all_tickets)} tickets')
    return all_tickets
