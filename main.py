import time
from interfacing import UI
from stages import Stages
import ledcontrol
import relaycontrol   

def main():
    ui = UI()
    stages = Stages(ui)

    relaycontrol.start()    

    NEXT_STAGE = {
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
                result = ui.end_screen()

                if result == "restart":
                    last_stage = None
                    ui.welcome_screen()
                    continue
                else:
                    break

    except KeyboardInterrupt:
        pass

    finally:
        relaycontrol.stop()      
        ui.cleanup()
        ledcontrol.leds_off()


if __name__ == "__main__":
    main()
