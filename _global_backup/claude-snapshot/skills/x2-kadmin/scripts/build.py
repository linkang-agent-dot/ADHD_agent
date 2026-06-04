from deploy import *
import getopt
import sys

branch_name = ""  # 需要更新的代码分支
tag_name = ""  # 需要构建的tag

class KaPostData:
    def __init__(self, access_key, names, src_type, src_target, execute_params, execute_images):
        self.accessKey = access_key
        self.name = names
        self.srcType = src_type
        self.srcTarget = src_target
        self.executeParams = execute_params
        self.executeImages = execute_images

    def to_dict(self):
        return {
            'accessKey': self.accessKey,
            'name': self.name,
            'srcType': self.srcType,
            'srcTarget': self.srcTarget,
            'executeParams': self.executeParams,
            'executeImages': self.executeImages
        }


def send_to_ka(name, src_type, src_target, execute_params, execute_images, success_str):
    access_key = access_keys["dev"]
    data = KaPostData(access_key, name, src_type, src_target, execute_params, execute_images)
    ka_url = apis["dev"]
    url = ka_url + "/api/workflow-key/execute"
    params = json.dumps(data.to_dict())
    headers ={
        "content-type":"application/json"
    }
    r = requests.post(url, headers = headers, data = params)
    res = json.loads(r.text)
    if res.get('error') is not None:
        print("params:", params, " res:", res)
    else:
        print(success_str)
        #print("gen_hotplugin " + plugin_type + " success")

def usage():
    print("build.py : build\n"
          "args:\n"
          " branch_name:     hotplugin branch name\n"
          " tag_name:        hotplugin tag name\n"
          " eg1:             python3 scripts/build.py --branch_name bugfix \n"
          " eg2:             python3 scripts/build.py --tag_name v1.2.3.4 \n")

def get_option():
    try:
        options, args = getopt.getopt(sys.argv[1:], "", ["branch_name=", "tag_name=", "help"])
        for name, value in options:
            print(name,value)
            if name == "--branch_name":
                global branch_name
                branch_name = value
            if name == "--tag_name":
                global tag_name
                tag_name = value
            if name == '--help':
                usage()
                return False
        return True
    except Exception as e:
        print("options error", e)
        usage()
        return False


def check_option():
    global branch_name
    global tag_name
    if branch_name == "" and tag_name == "":
        print("branch_name 或 tag_name 不能为空")
        return False
    return True


def main():
    if get_option() == False or check_option() == False:
        return
    global branch_name
    global tag_name
    name = "x2gs_构建_game"
    names = [name]
    if branch_name != "":
        success_str = "gs-构建任意"+ branch_name +" success"
        send_to_ka(names, "branch", branch_name, "", "", success_str)
    else:
        success_str = "gs-构建任意"+ tag_name +" success"
        send_to_ka(names, "tag", tag_name, "", "", success_str)

if __name__ == '__main__':
    main()