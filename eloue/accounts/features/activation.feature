Feature: Activate my account
  In order to access the website
  As an inactive user
  I want to be able to activate my account
  
  Background:
    Given I am user benjamin
    And my account is inactive
  
  Scenario: Activate inactive user
    Given I've created my account 2 days ago
    When I activate my account
    Then I should see a welcome message
    And I should be able to login
  
  Scenario: Activate expired inactive user
    Given I've created my account 9 days ago
    When I activate my account
    Then I should see a error message
    Then I should not be able to login

    