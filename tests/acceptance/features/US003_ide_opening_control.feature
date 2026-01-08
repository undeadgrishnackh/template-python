@US-003 @ide-control @automation-safe
Feature: IDE Opening Control
  As a 5D-Wave agent, CI/CD pipeline, or developer with IDE preferences
  I want to control whether and which IDE opens after scaffold generation
  So that headless automation works and developers use their preferred editor

  Background:
    Given the cookiecutter template is available

  # Happy Path Scenarios - Automation Safe

  @happy-path @default-none @agentic-workflow
  Scenario: Default behavior is no IDE for safe automation
    Given Alex is the 5D-Wave agent running in automated mode
    When Alex generates a scaffold with directory name "source"
    And no IDE parameter is specified
    Then no IDE application launches
    And the terminal returns control to the calling process immediately
    And Alex continues the automated workflow without interruption

  @happy-path @explicit-none
  Scenario: Explicit none parameter ensures no IDE opens
    Given a CI/CD pipeline is generating a scaffold
    When the pipeline runs cookiecutter with IDE option "none"
    Then no IDE launch is attempted
    And the process completes cleanly for pipeline execution

  # Happy Path Scenarios - Developer Preferences

  @happy-path @vscode
  Scenario: Developer requests VS Code opening
    Given Sam is developing interactively on their workstation
    And VS Code is installed with the code CLI available
    When Sam generates a scaffold with IDE option "vscode"
    Then VS Code opens with the generated project directory
    And Sam can start coding immediately in their preferred editor

  @happy-path @pycharm
  Scenario: Developer requests PyCharm opening
    Given Raj prefers PyCharm for Python development
    And PyCharm is installed on the system
    When Raj generates a scaffold with IDE option "pycharm"
    Then PyCharm opens with the generated project directory
    And the appropriate platform command is used for the operating system

  @happy-path @pycharm-macos
  Scenario: PyCharm opens correctly on macOS
    Given Kim is developing on macOS
    And PyCharm is installed as a macOS application
    When Kim generates a scaffold with IDE option "pycharm"
    Then the hook uses the macOS open command for PyCharm
    And PyCharm application launches with the project

  # Error Handling Scenarios - Non-Fatal IDE Failures

  @error-path @vscode-not-installed @non-fatal
  Scenario: VS Code command not found is non-fatal
    Given a developer requests VS Code opening
    And the VS Code CLI is not installed or not in PATH
    When the developer generates a scaffold with IDE option "vscode"
    Then the hook prints a warning about VS Code not being found
    But the scaffold generation completes successfully
    And the exit code is zero indicating success
    And all other operations completed normally

  @error-path @pycharm-not-installed @non-fatal
  Scenario: PyCharm command not found is non-fatal
    Given a developer requests PyCharm opening
    And PyCharm is not installed on the system
    When the developer generates a scaffold with IDE option "pycharm"
    Then the hook prints a warning about PyCharm not being found
    But the scaffold generation completes successfully
    And the developer can open the project manually

  @error-path @ide-timeout @non-fatal
  Scenario: IDE launch timeout does not block completion
    Given a developer requests VS Code opening
    And VS Code is installed but hangs on launch
    When the developer generates a scaffold with IDE option "vscode"
    Then the hook times out the IDE launch after a reasonable period
    And the scaffold generation completes with a warning
    And the process does not hang indefinitely

  # Error Handling Scenarios - Fatal Validation Errors

  @error-path @invalid-ide-option @fatal
  Scenario: Invalid IDE option rejected with helpful error
    Given a developer specifies an unsupported IDE
    When the developer runs cookiecutter with IDE option "vim"
    Then the hook fails immediately with a clear error
    And the error message lists valid options: none, vscode, pycharm
    And no scaffold generation begins
    And no files are created or modified

  @error-path @typo-in-option @fatal
  Scenario: Typo in IDE option caught early
    Given a developer accidentally types "vcode" instead of "vscode"
    When the developer runs cookiecutter with IDE option "vcode"
    Then the hook fails with an error about invalid IDE option
    And the error suggests "vscode" as a possible correction
    And the developer can retry with the correct option

  # Integration Scenarios

  @integration @ide-with-git-detection
  Scenario: IDE control works with git detection
    Given Alex is in an existing git repository
    And Alex wants no IDE to open for automation
    When Alex generates a scaffold with directory name "source" and IDE option "none"
    Then git repository detection works correctly
    And scaffold generation completes
    And no IDE opens
    And the agent workflow continues uninterrupted

  @integration @ide-with-directory-name
  Scenario: IDE control works with custom directory name
    Given Maria provides directory name "trading-engine"
    And Maria wants VS Code to open for development
    When Maria generates the scaffold with IDE option "vscode"
    Then the scaffold is created in "trading-engine" directory
    And VS Code opens with the "trading-engine" directory
    And both features work together correctly
