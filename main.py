import asyncio
from RPi import GPIO
from asyncua import ua, uamethod, Server

light_pin_red = 16
light_pin_green = 20
light_pin_blue = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(light_pin_red, GPIO.OUT)
GPIO.setup(light_pin_green, GPIO.OUT)
GPIO.setup(light_pin_blue, GPIO.OUT)
GPIO.setwarnings(False)

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://10.4.1.128:4840")
    server.set_server_name("Server Led")
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity
        ]
    )
    uri = "http://motter"
    idx = await server.register_namespace(uri)

    LED1_node = await server.nodes.objects.add_object(idx, "LED1")
    rouge_node = await LED1_node.add_variable(idx, "Rouge", False)
    green_node = await LED1_node.add_variable(idx, "Green", False)
    blue_node = await LED1_node.add_variable(idx, "Blue", False)
    await rouge_node.set_writable(True)
    await green_node.set_writable(True)
    await blue_node.set_writable(True)
    await LED1_node.add_variable(idx, "FermerLumiere", True)

    async def async_toggle_fermerLumiere(parent_node_id):
        parent_node = server.get_node(parent_node_id)
        fermerLumiere_node = await parent_node.get_child([str(idx) + ":FermerLumiere"])
        fermerLumiere = await fermerLumiere_node.read_value()
        await fermerLumiere_node.write_value(not fermerLumiere)
        print("Lumières fermées : " + str(fermerLumiere))
        if fermerLumiere == True:
            await rouge_node.write_value(True)
            await blue_node.write_value(True)
            await green_node.write_value(True)
        else:
            await rouge_node.write_value(False)
            await blue_node.write_value(False)
            await green_node.write_value(False)


    def toggle_fermer_lumiere(parent_node_id):
        asyncio.run(async_toggle_fermerLumiere(parent_node_id))

    toggle_is_running_node = await LED1_node.add_method(
        idx,
        "toggleFermerLumiere",
        toggle_fermer_lumiere,
        [],
        [],
    )

    async with server:

        while True:
            # Read the values of the OPC UA variables
            red_value = await rouge_node.read_value()
            green_value = await green_node.read_value()
            blue_value = await blue_node.read_value()

            # Update the GPIO pins based on the variable values
            GPIO.output(light_pin_red, red_value)
            GPIO.output(light_pin_green, green_value)
            GPIO.output(light_pin_blue, blue_value)
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        GPIO.cleanup()

