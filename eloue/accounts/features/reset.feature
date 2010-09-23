Feature: Reset password
  Scenario: Reset my password 
    When I navigate to page 'password_reset'
    Then I should find 'form'
    Given I fill 'email' field with 'alexandre.woog@e-loue.com'
    When I submit to page 'password_reset'
    Then I should be redirected to page 'password_reset_done' with code 302
    And I should have received 1 email
