from docassemble.base.util import user_info, get_config, interview_menu, interview_url, user_logged_in
from typing import List, Tuple, Optional, Dict

"""
This module provides a function to get a list of interviews that the current user is allowed to distribute.

The `get_distributable_interviews()` function filters the list of interviews based on the current user's privileges and email.

It expects a global configuration that looks like this:

interview manager interviews:
  - name: docassemble.MyPackage:my_interview_1.yml
    allowed_distributors:
      - privilege1
      - user1@example.com
  - name: docassemble.MyPackage:my_interview_2.yml
    allowed_distributors:
      - privilege2
      - user2@example.com
  - name: docassemble.MyPackage:my_interview_3.yml
    allowed_distributors:  # Empty list means no restrictions
"""

__all__ = ['get_distributable_interviews', 'can_distribute_interview', "interview_url_with_owner"]

def can_distribute_interview(interview: Dict[str, List[str]], user_privileges: List[str], user_email:str) -> bool:
    """
    Checks if the specified user can distribute a specific interview.

    Args:
        interview (dict): The configuration dictionary for the specific interview.
        user_privileges (list): The user's privileges.
        user_email (str): The user's email address.
    """
    allowed_distributors = interview.get('allowed_distributors', [])
    # If no specific distributors are defined, allow anyone
    if not allowed_distributors:
        return True
    # Check if the user's email or any of their privileges is allowed
    return any(dist in allowed_distributors for dist in (user_privileges + [user_email]))

def get_distributable_interviews(configuration_path:str = "interview manager interviews") -> List[Tuple[str, str]]:
    """
    Filters the list of interviews that can be distributed based on the current user's privileges and email.
    Additionally returns interviews that appear in the `interview_menu()` as a tuple
    of (display name, internal name).

    interview manager interviews:
    - name: docassemble.MyPackage:my_interview_1.yml
        allowed_distributors:
        - privilege1
        - user1@example.com
    - name: docassemble.MyPackage:my_interview_2.yml
        allowed_distributors:
        - privilege2
        - user2@example.com
    - name: docassemble.MyPackage:my_interview_3.yml
        allowed_distributors:  # Empty list means no restrictions

    Returns:
        list: A filtered list of interviews the current user is allowed to distribute.
              Each entry is a tuple: (display name, internal name).
    """
    # Get the interviews configuration from the Docassemble config
    interviews_list = get_config(configuration_path, [])
    
    # If no interviews are configured, return an empty list
    if not interviews_list:
        return []
    
    # Get the current user's privileges and email
    user_privileges = user_info().privileges or []
    user_email = user_info().email
    
    # Get the available interviews from interview_menu()
    menu_interviews = interview_menu()

    # Create a dictionary mapping filenames to their display names
    menu_interview_map = {interview['filename']: interview['title'] for interview in menu_interviews}

    # Filter the interviews where the user can distribute
    distributable_interviews = []
    for interview in interviews_list:
        if can_distribute_interview(interview, user_privileges, user_email):
            internal_name = interview.get('name')
            # Check if the interview is in the menu and get the display name
            display_name = menu_interview_map.get(internal_name, internal_name)  # Use internal name if no display name found
            distributable_interviews.append((internal_name, display_name))
    
    return distributable_interviews


def interview_url_with_owner(filename: str, valid_days:int=14, interview_metadata_owner: Optional[str] = None) -> str:
    """
    Returns a launch link for the specified interview with an embedded metadata "owner".

    This can be used later to filter the interviews based on the metadata owner, typically in a situation
    where multiple advocates need to track the interviews they distribute.

    Args:
        filename (str): The internal name of the interview.
        interview_metadata_owner (str): The metadata owner to embed in the launch link.
        valid_days (int): The number of hours the interview should be available. Used primarily to obfuscate the interview URL.

    Returns:
        str: The launch link for the interview.
    """
    if not interview_metadata_owner:
        if user_logged_in():
            interview_metadata_owner = user_info().email
        else:
            interview_metadata_owner = None
    if valid_days is None:
        return interview_url(i=filename, interview_metadata_owner=interview_metadata_owner, style="short")
    return interview_url(i=filename, interview_metadata_owner=interview_metadata_owner, style="short", temporary=valid_days*24)