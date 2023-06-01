import socket
from time import sleep
from threading import Thread
import asyncio
import os

IP, DPORT = 'localhost', 8080
directory_path = "./myfiles"


# Helper function that converts integer into 8 hexadecimal digits
# Assumption: integer fits in 8 hexadecimal digits
def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)

async def recv_message(reader: asyncio.StreamReader):
    full_data = await reader.readline()
    return full_data.decode()
    



async def send_message(writer: asyncio.StreamWriter, data):
    await asyncio.sleep(1)

    writer.write(to_hex(len(data)).encode())
    writer.write(data.encode())

    await writer.drain()


async def connect(i):
    reader, writer = await asyncio.open_connection(IP, DPORT)
    # TODO: receive the introduction message by implementing `recv_intro_message` above.
    intro = await recv_message(reader)
    print(intro)

    count = 0
    while count < 3:
        password = input("Enter password: ")
        await send_message(writer, password)
        stat = await recv_message(reader)
        # print(f"Count : {count}")
        print(stat)
        if stat == "Sucessfully login.....\n":
            break
        else:
            count += 1

    if count == 3:
        print("Maximum number of attempts reached.")


    while True:
        user_request = input("What server you want: ")
        await send_message(writer, user_request)
        request_ack = await recv_message(reader)

        if user_request == "close":
            print("Closing connection to the server.....")
            break
        elif request_ack[:3] == "NAK":
            print(request_ack)
        elif user_request == "list":
            print(request_ack)
            list_info = await recv_message(reader)
            print(list_info)

        elif user_request[:4] == "put ":
            # check if the file is in the client file 
            print(request_ack)
            file_name = user_request[4:]
            current_file = str(os.listdir(directory_path))
            if file_name in current_file:
                #send the file name first
                await send_message(writer, file_name)
                # send the content of file 
                file_name = "./myfiles/" + file_name
                file = open(file_name, "r")
                file_content = str(file.read()) + "\n"
                await send_message(writer, file_content)
            else:
                await send_message(writer, "No such file\n")
                print("No such file: " + file_name)

        elif user_request[:4] == "get ":
            print(request_ack)
            file_name = user_request[4:]
            # print("Server have the file")
            file_content =  await recv_message(reader)
            # print(file_content)
            file_name = "./myfiles/" + file_name
            file = open(file_name, "w")
            file.write(file_content) 
            file.flush()
            file.close()

        elif user_request[:7] == "remove ":
            print(request_ack)






    return 0

async def main():
    tasks = []
    tasks.append(connect(str(0).rjust(8, '0')))

    await asyncio.gather(*tasks)
    print("done")

# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())
