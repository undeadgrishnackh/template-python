import sys

from pytest_bdd import given, when, then, scenarios

from modules import dummy


scenarios("../features/0_dummy_runs.feature")


@given("a user")
def give_a_developer(mocker):
    mocker.resetall()


@when("he/she runs the tests", target_fixture="installer")
def installer(capsys):
    return_code = dummy.print_the_title()
    out, err = capsys.readouterr()
    return return_code, out.strip(), err.strip()


@then("a dummy title should be printed")
def then_the_title_is_printed(installer):
    return_code, out, err = installer
    assert "😊 Welcome to Dummy Kata" in out
