#This script can be used to test z-offsets for moving our custom labware
#This script uses the protocol.move_labware () method to actually move labware with custom defined z-offsets, to determine the right offsets for our custom labware.
#Make sure to use python 3.10, as other versions can cause conflicts

#################### Helpful links: ################################
#All information about Opentrons python API v2: https://docs.opentrons.com/v2/index.html
#Commands for liquid control: https://docs.opentrons.com/v2/basic_commands/liquids.html#liquid-control

from opentrons import protocol_api
metadata = {"protocolName": "Sandbox_test_gripper_Noel",
            "description": """Sandbox test to test custom z-offsets for Flex gripper. Move a Greiner 96-well plate.""",
            "author": "Noel"}

requirements = {"robotType": "Flex", "apiLevel": "2.23"}

############## RUN TIME PARAMETER FOR EASILY CHANGING Z-OFFSET AT START OF PROTOCOL ################
def add_parameters(parameters: protocol_api.ParameterContext):
    parameters.add_int(
        variable_name='micrometers',
        display_name='z-offset',
        description='How many micrometers should the z-offset be?',
        default=0,
        minimum=-10,
        maximum=20,
        unit='µL'
    )



def run(protocol: protocol_api.ProtocolContext):

    #Load Heater-Shaker module in slot D1
    hs_mod = protocol.load_module(module_name='heaterShakerModuleV1', location="D1")
    #Load Temp. Module V2 in slot C1
    temp_mod = protocol.load_module(module_name="temperature module gen2", location="C1")
    #Don't forget to add the method "load_adapter()" here, if you use an adapter
    #If you have labware on the module, add the following line: temp_mod= load_labware("greiner_96_wellplate_340ul.json", "C1")

    #Load reservoir in slot C2
    #reservoir = protocol.load_labware("integra300ml_reservoir", location="C2")

    #Load Greiner 96-well plate in slot D2
    sample_plate = protocol.load_labware("greiner_96_well_plate_655090", location="D2")

    #Load Trash in Slot A3 (STANDARD)
    trash = protocol.load_trash_bin("A3")

    #Loading tipracks left in script, in case this is required
    # Load 200ul tiprack Nr. 1 + 2 in slots B2 + B3 along with adapters
    # Load adapter in B2, then tiprack onto that adapter
    adapter1 = protocol.load_adapter("opentrons_flex_96_tiprack_adapter", "B2")
    tips200_1 = adapter1.load_labware("opentrons_flex_96_filtertiprack_200ul")
    # Load adapter in B3, then tiprack onto that adapter
    adapter2 = protocol.load_adapter("opentrons_flex_96_tiprack_adapter", "B3")
    tips200_2 = adapter2.load_labware("opentrons_flex_96_filtertiprack_200ul")

    #Load Flex 96-ch pipette
    pipette = protocol.load_instrument("flex_96channel_1000", tip_racks=[tips200_1, tips200_2], liquid_presence_detection=False)

    #Flex gripper does not have to be loaded, but is accessed via the "protocol.move_labware()" method.
    #Move above the labware with a custom z offset
    #The "pick_up_offset={"z": -5}" allows you to apply a custom Z-offset in mm from the top of the labware.
    #If z-offset=0 the gripper will attempt to grip from the labware's top, defined in the labware definition (the default behaviour).
    #This means, if the Flex grips your plate exactly in the middle, when running a protocol from protocol designer for example,
    #you will have to add a positive z-offset value, to grip the plate higher/further away from the deck.
    #A negative z-offset value makes the gripper move deeper i.e. closer down toward the deck.
    #A positive z-offset value makes the gripper move further away from the deck
    protocol.move_labware (
        labware=sample_plate,
        new_location='C3',
        use_gripper=True,
        pick_up_offset={'x': 0, 'y': 0, 'z': 3}
    )