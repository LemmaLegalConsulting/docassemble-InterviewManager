# ALDashboard static draft reviewed against the get_link/no-email path.
Feature: Share an interview link

  Scenario: Create a sharing link without sending email
    Given the maximum seconds for each step is 60
    And I sign in with the email "DA_ADMIN_EMAIL" and the password "DA_ADMIN_PASSWORD"
    And I start the interview at "manager.yml"
    And I get to the question id "sharing link ready" with this data:
      | var | value |
      | action_to_take | get_link |
      | selected_interview | docassemble.InterviewManager:manager.yml |
      | valid_days | 14 |
    Then I should see the phrase "Here is your sharing link"
    And I should see the phrase "Right-click and copy this link to share it with your client"
