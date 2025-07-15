


######################################################################################################### DESCRIPTION AND EXPLANATIONS ####################################################################################################################################



################### DESCRIPTION ############################
# This script serves as a basic template for OT-Flex protocols and as a sandbox to play around in
# Make sure to use python 3.10, as other versions can cause conflicts

################### HOW TO CORRECTLY LOAD TIP BOXES ON OT-FLEX #########################
# As all tip boxes on the OT-Flex require a tip-box adapter to be placed directly on the deck, both have to be loaded in your OT-Flex python protocols.
# Make sure not to load the adapter and the tip-box into the same slot on the deck as in the following example:
# Adapter1 = protocol.load_adapter(load_name="opentrons_flex_96_tiprack_adapter", location="B2")
# tips200_1 = protocol.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location="B2")  # ❌ Conflict!

################### INSTEAD DO THE FOLLOWING ##########################
# Explained in words: You need to load the adapter first, and then load the tiprack onto the adapter, like so:
# Load adapter in B2, then tiprack on that adapter
# adapter1 = protocol.load_adapter("opentrons_flex_96_tiprack_adapter", "B2")
# tips200_1 = adapter1.load_labware("opentrons_flex_96_filtertiprack_200ul")

#################### HELPFUL LINKS: ################################
# All information about Opentrons python API v2: https://docs.opentrons.com/v2/index.html
# Commands for liquid control: https://docs.opentrons.com/v2/basic_commands/liquids.html#liquid-control

############ GENERAL TRANSFER ADVICE ################
# When coding transfers, always remember:
# Give source and destination wells/columns/rows correctly as python is 0 indexed.
# Example: When entering a destination "row[1]" -> this will actually target column 2!
# When performing a transfer on the Flex, using the 96-channel pipette, always target well 'A1', as you would crash the pipet otherwise.

############ ONLYTRANSFER HELPER FUNCTION ###############
# The Onlytransfer helper function acts as an alternative to the standard "transfer" method, which is built into the API by Opentrons.
# The standard "transfer" method takes some arguments from the user and then automatically picks up tips, performs the transfer from source to destination and automatically trashes the tips in the trash ['A3'] Deck slot.
# As you might not want to automatically pick up a new set of tips each time you perform a transfer and as you might not want to actually trash your tips, I have created the "Onlytransfer" helper function.
# The Onlytransfer helper function does not include any automatic tip handling and also let's you define many more parameters individually, compared to the standard "transfer" method.

# An example of parameters, which you can control with my helper function, but cannot change, when using the standard "transfer" method of the Opentrons API:
# Individual aspiration and dispensing speeds for mixing
# Individual aspiration and dispensing speeds for transfer
# Individual aspiration and dispensing heights for mixing
# Individual aspiration and dispensing heights for transfer

# The Onlytransfer helper function is defined in this template below and doesn't need to be defined by you.

############# HOW TO IMPLEMENT/USE THE ONLYTRANSFER FUNCTION ##################
# Please see in the template protocol below.

################ TIP HANDLING COMMANDS #################
# Tell Flex to pick up tips without any arguments below. When you add this to your protocol, this statement works because the API knows which tip rack is associated with pipette, as indicated by "tip_racks=[tiprack_1] in the load_instrument call.
# pipette.pick_up_tip()

# Tell Flex to return used tips to their original location. The API considers tips as "used" after being picked up. This means the Flex will not pick up tips again, once they have been returned to their tip-rack.
# pipette.return_tip()

# Tell Flex to trash tips in the trash bin without any arguments. If you want to drop your tips into a tip-rack, simply add a location parameter (see second example below)
# pipette.drop_tip(trash)
# pipette.drop_tip(tiprack1['A1'])



################################################################################################################ TEMPLATE PROTOCOL BELOW #################################################################################################################################


# Start of every OT-Flex protocol:
from opentrons import protocol_api
metadata = {"protocolName": "Sandbox_test_transfer_and_gripper_Noel",
            "description": """Sandbox test to test custom z-offsets for Flex gripper. Move a Greiner 96-well plate.""",
            "author": "Noel"}

# Remember to always include a "Requirements" section for OT-flex protocols and check that your software matches those.
requirements = {"robotType": "Flex", "apiLevel": "2.23"}

# Initiate protocolcontext:
def run(protocol: protocol_api.ProtocolContext):

    # Load Heater-Shaker module in slot D1
    hs_mod = protocol.load_module(module_name='heaterShakerModuleV1', location="D1")
    # Load Temp. Module V2 in slot C1
    temp_mod = protocol.load_module(module_name="temperature module gen2", location="C1")
    # Don't forget to add the method "load_adapter()" here, if you use an adapter
    # If you have labware on the module, add the following line: temp_mod= load_labware("greiner_96_wellplate_340ul.json", "C1")

    # Load reservoir in slot C2
    reservoir = protocol.load_labware("integra300ml_reservoir", location="C2")
    # Load Greiner 96-well plate in slot D2
    sample_plate = protocol.load_labware("greiner_96_well_plate_655090", location="D2")
    # Load Trash in Slot A3 (STANDARD, NEVER CHANGE THIS)
    trash = protocol.load_trash_bin("A3")

    # Load 200ul tiprack Nr. 1 + 2 in slots B2 + B3 along with adapters
    # Load adapter in B2, then tiprack onto that adapter
    adapter1 = protocol.load_adapter("opentrons_flex_96_tiprack_adapter", "B2")
    tips200_1 = adapter1.load_labware("opentrons_flex_96_filtertiprack_200ul")
    # Load adapter in B3, then tiprack onto that adapter
    adapter2 = protocol.load_adapter("opentrons_flex_96_tiprack_adapter", "B3")
    tips200_2 = adapter2.load_labware("opentrons_flex_96_filtertiprack_200ul")

    # Load Flex 96-ch pipette
    pipette = protocol.load_instrument("flex_96channel_1000", tip_racks=[tips200_1, tips200_2], liquid_presence_detection=False)

    ##################### ONLYTRANSFER HELPER FUNCTION FOR CODING PURE TRANSFERS, WITHOUT TIP PICKUP OR TRASHING: #############################

    def Onlytransfer(
            pipette,
            volume,
            source,
            destination,
            mix_before=None,  # Tuple: (reps, volume)
            mix_after=None,  # Tuple: (reps, volume)
            mix_before_height=None,  # mm from bottom
            mix_after_height=None,  # mm from bottom
            blow_out=False,
            blow_out_location='destination',  # 'source', 'destination', 'trash'
            transfer_aspirate_speed=None,  # µL/s
            transfer_dispense_speed=None,  # µL/s
            mix_aspirate_speed=None,  # µL/s
            mix_dispense_speed=None,  # µL/s
            air_gap_volume=0,  # µL
            touch_tip_after_aspirate=False,
            touch_tip_after_dispense=False,
            delay_after_aspirate=0,
            delay_after_dispense=0,
            aspirate_height=None,  # mm from bottom
            dispense_height=None  # mm from bottom
    ):
        """
        Custom OT-Flex liquid transfer function with full control over:
        - Speeds (individual mixing and transfer speeds)
        - Heights (individual for mixing and transfer)
        - Air gaps
        - Mix before/after
        - Delays
        - No tip handling
        """

        # Backup original speeds
        original_aspirate = pipette.flow_rate.aspirate
        original_dispense = pipette.flow_rate.dispense

        # MIX BEFORE
        if mix_before:
            reps, mix_vol = mix_before
            if mix_aspirate_speed is not None:
                pipette.flow_rate.aspirate = mix_aspirate_speed
            if mix_dispense_speed is not None:
                pipette.flow_rate.dispense = mix_dispense_speed
            mix_loc = source.bottom(mix_before_height) if mix_before_height else source.bottom(1)
            pipette.mix(reps, mix_vol, mix_loc)

        # TRANSFER SPEED SETTING
        if transfer_aspirate_speed is not None:
            pipette.flow_rate.aspirate = transfer_aspirate_speed
        if transfer_dispense_speed is not None:
            pipette.flow_rate.dispense = transfer_dispense_speed

        # ASPIRATE
        asp_loc = source.bottom(aspirate_height) if aspirate_height else source.bottom()
        pipette.aspirate(volume, asp_loc)

        if delay_after_aspirate > 0:
            pipette.delay(seconds=delay_after_aspirate)

        if air_gap_volume > 0:
            pipette.air_gap(air_gap_volume)

        if touch_tip_after_aspirate:
            pipette.touch_tip(source)

        # DISPENSE
        disp_loc = destination.bottom(dispense_height) if dispense_height else destination.bottom()
        pipette.dispense(volume + air_gap_volume, disp_loc)

        if delay_after_dispense > 0:
            pipette.delay(seconds=delay_after_dispense)

        if touch_tip_after_dispense:
            pipette.touch_tip(destination)

        # MIX AFTER
        if mix_after:
            reps, mix_vol = mix_after
            if mix_aspirate_speed is not None:
                pipette.flow_rate.aspirate = mix_aspirate_speed
            if mix_dispense_speed is not None:
                pipette.flow_rate.dispense = mix_dispense_speed
            mix_loc = destination.bottom(mix_after_height) if mix_after_height else destination.bottom(1)
            pipette.mix(reps, mix_vol, mix_loc)

        # BLOW OUT
        if blow_out:
            if blow_out_location == 'source':
                pipette.blow_out(source.top())
            elif blow_out_location == 'destination':
                pipette.blow_out(destination.top())
            elif blow_out_location == 'trash':
                pipette.blow_out()

        # RESET speeds
        pipette.flow_rate.aspirate = original_aspirate
        pipette.flow_rate.dispense = original_dispense

################## MOVE LABWARE WITH CUSTOM Z OFFSET #########################
    # The "pick_up_offset={"z": -5}" allows you to apply a custom Z-offset in mm from the top of the labware.
    # If z-offset=0 the gripper will attempt to grip from the labware's top, defined in the labware definition (the default behaviour, most often targets middle section of labware).
    # This means, if the Flex grips your plate exactly in the middle, when running a protocol from protocol designer for example,
    # you will have to add a positive z-offset value, to grip the plate higher/further away from the deck.
    # A negative z-offset value makes the gripper move deeper i.e. closer down toward the deck.
    # A positive z-offset value makes the gripper move further away from the deck.
    # Remember to always give the x + y offsets as well, even if they are 0, otherwise the protocol will fail. x + y offsets should always be 0!

    protocol.move_labware (
        labware=sample_plate,
        new_location='C3',
        use_gripper=True,
        pick_up_offset={'x': 0, 'y': 0, 'z': 2}
    )

# Turning lights on and off 2x
    protocol.set_rail_lights(False)
    protocol.set_rail_lights(True)
    protocol.set_rail_lights(False)
    protocol.set_rail_lights(True)

################ EXAMPLE FOR LIQUID TRANSFER USING NEW HELPER FUNCTION: ################################

# First pick up tips
    pipette.pick_up_tip()

# Actual transfer
    Onlytransfer(
      pipette=pipette,
      volume=200,
      source=reservoir['A1'],
      destination=sample_plate['A1'],
      mix_before=(2, 100),
      mix_before_height=8,
      mix_after=(2, 100),
      mix_after_height=1.5,
      transfer_aspirate_speed=100,
      transfer_dispense_speed=50,
      mix_aspirate_speed=100,
      mix_dispense_speed=100,
      aspirate_height=8,
      dispense_height=1.5,
      blow_out=False,
     air_gap_volume=0
     )



        # Remember to trash or return your tips to tip box
        # Returning tips to tip box
    pipette.return_tip()