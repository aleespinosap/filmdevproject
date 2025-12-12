#main.py

import time
from interfacing import UI
from stages import Stages
import ledcontrol
import relaycontrol

def main():
    """
    This function intializes the user interface (UI) and the stage control (Stages)
    It starts the threading for the relay control, and forces the stage order so that
    the user cannot repeat or enter the wrong stage at any point. The stages are
    continuous so the program can't be exited until all 4 have been completed, unless Ctrl+C
    is pressed.
    """
    ui = UI()
    stages = Stages(ui)

    relaycontrol.start()

    NEXT_STAGE = {#Dictionary that enforces strict stage order
        None: 1,  # start -> dev
        1: 2,     # dev -> stop
        2: 3,     # stop -> fixer
        3: 4,     # fixer -> photoflo
        4: None   # photoflo -> done
    }

    last_stage = None

    try:
        ui.welcome_screen()

        while True:
            choice = ui.wait_for_button()
            correct = NEXT_STAGE[last_stage]

            if correct is None:
                break

            if choice != correct:
                ui.clear()
                ui.write_line("Invalid stage!", 2)
                time.sleep(1)
                ui.stage_done_screen()
                continue

            if choice == 1:
                dev_seconds, choice_level = ui.development_settings(
                    stages.dev_run_seconds,
                    stages.push_pull_options,
                    stages.dev_choice_level,
                )
                stages.set_dev_settings(dev_seconds, choice_level)

                stages.wash_dev()
                last_stage = 1
                ui.stage_done_screen()

            elif choice == 2:
                stages.stopdev()
                last_stage = 2
                ui.stage_done_screen()

            elif choice == 3:
                stages.wash_fix()
                last_stage = 3
                ui.stage_done_screen()

            elif choice == 4:
                stages.wash_photoflo()
                last_stage = 4
                ui.end_screen()
                last_stage = None
                ui.welcome_screen()
                continue

    except KeyboardInterrupt:
        pass

    finally:
        relaycontrol.stop()
        ui.cleanup()
        ledcontrol.leds_off()


if __name__ == "__main__":
    main()

