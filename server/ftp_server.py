import socket
import asyncio
import os

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100
correct_password = "123456"
directory_path = "./myfiles"


async def send_message(writer,data):
    writer.write(data.encode())
    await writer.drain()


async def receive_message(reader: asyncio.StreamReader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = await reader.readexactly(8)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    full_data = await reader.readexactly(data_length)
    return full_data.decode()




    

    

async def handle_client(reader, writer):
    intro_message = "Hello! Please enter the password to connect the server\n"
    await send_message(writer,intro_message)

    count = 0
    while count < 3:
        password = await receive_message(reader)
        print("received: " +  password)
        if password == correct_password:
            await send_message(writer, "Sucessfully login.....\n")
            break
        else:
            await send_message(writer, "Incorrect password.....\n")
            count += 1
    
    if count >= 3:
        await send_message(writer, "Maximum number of attempts reached. Closing the server...\n")
        writer.close()
        await writer.wait_closed()

    # handle FTP servies here
    while True:
        client_request = await receive_message(reader)
        print("The client request :" + client_request)
        # Handling request


        if client_request == "list":
            """
            List all item in myfiles, no need ACK or NAK
            """
            await send_message(writer, "ACK: list\n")
            list_info = os.listdir(directory_path)
            list_info = str(list_info)
            list_info = list_info + "\n"
            await send_message(writer, list_info)

        elif client_request[:4] == "put ":

            """
            Put the file from client to server, handle error in client side
            """
            await send_message(writer, "ACK: put\n")
            # get file name
            file_name = await receive_message(reader)
            if file_name != "No such file\n":
                file_name = "./myfiles/" + file_name
                file = open(file_name, "w")
                file_content = await receive_message(reader)
                # print(file_content)
                # print(type(file_content))
                file.write(file_content) 
                file.flush()
                file.close()

        elif client_request[:4] == "get ":
            """
            Send the file to the client side
            ACK if the file exists
            NAK if the file is not exists
            """
            # await send_message(writer, "ACK: get\n")
            file_name = client_request[4:]
            # print("Get File: :" + file_name)
            current_file = str(os.listdir(directory_path))
            if file_name in current_file:
                print("server have the file")
                await send_message(writer, "ACK: get\n")
                file_name = "./myfiles/" + file_name
                file = open(file_name, "r")
                file_content = str(file.read()) + "\n"
                await send_message(writer, file_content)
            else:
                await send_message(writer,"NAK: no such file to get\n")



        elif client_request[:7] == "remove ":
            """
            Remove the file on myfiles
            ACK if the file exists
            NAK if the file is not exists
            """
            file_name = client_request[7:]
            current_file = str(os.listdir(directory_path))
            if file_name in current_file:
                await send_message(writer, "ACK: remove\n")
                file_name = "./myfiles/" + file_name
                os.remove(file_name)
            else:
                await send_message(writer,"NAK: no such file to remove\n")
                
        elif client_request == "close":
            print("Connection close....")
            break
        else:
            await send_message(writer, "NAK: unknown command\n")




    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(
            handle_client,
            INTERFACE, SPORT
    )

    async with server:
        await server.serve_forever()

# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())
