import zipfile, time, os

class Compress:

    @classmethod
    def zip(cls, input_path):
        input_path = './output/'
        list = os.scandir(input_path)
        zip_name = 'gif'+ str(time.time()) +'.zip'
        for file in list:
            if file.name.endswith('.gif') and file.name != 'uploaded.gif':
                zipf = zipfile.ZipFile(zip_name, 'a', zipfile.ZIP_DEFLATED)
                zipf.write(file.path)
                zipf.close()

        return zip_name
        