import sys
import pickle
import olx_find_all_brands_and_models
import compare_models

feats_dic = {
    "standv":
        {"segmento": ["pequeno citadino", "citadino", "utilitário", "sedan", "carrinha", "monovolume", "suv/tt",
                      "cabrio", "coupé"],
         "combustivel": ["gasolina", "diesel", "gpl", "eléctrico", "híbrido (gasolina)", "híbrido (diesel)"],
         "tipo de caixa": ["manual", "automática", "semi-automática"],
         "traccao": ["integral", "traseira", "dianteira"]
         },
    "olx":
        {"": None},
    "volantesic":
        {"segmento": ["cabrio", "desportivo/coupé", "utilitário", "citadino", "sedan", "carrinha", "monovolume",
                      "suv/tt"],
         "combustivel": ["gasolina", "híbrido", "diesel", "gpl", "eléctrico"],
         "tipo de caixa": ["automático", "manual", "semi-automático"],
         "traccao": ["2x4", "4x2", "4x4"]
         }
}


def from_type_c_to_src_and_dest(type_c):
    if type_c == "standv_volantesic":
        src = "standv"
        dest = "volantesic"
    elif type_c == "olx_volantesic":
        src = "olx"
        dest = "volantesic"
    else:
        print("error creating associations, src and dest invalid")
    return src, dest


def create_associations(type_c):
    """

    :param type_c: src and dest choice
    :return: dictionary with all the associations, already auto associated
    """
    t_dic = {}
    src, dest = from_type_c_to_src_and_dest(type_c)
    src_feats = feats_dic[src]
    dest_feats = feats_dic[dest]
    for feat_type in src_feats:
        t_dic[feat_type] = {}

    for feat_type in dest_feats:
        # turn into dictionary
        new_dic = {}
        for i in dest_feats[feat_type]:
            new_dic[i] = 0
        dest_feats[feat_type] = new_dic
        # print(dest_feats)
        for feat in src_feats[feat_type]:
            t_dic[feat_type][feat] = dest_feats[feat_type]
    # print(t_dic)
    auto_associations(t_dic)
    pickle_save(t_dic, type_c)
    return t_dic


def auto_associations(t_dic):
    """
    transformation on input dic
    :param t_dic: dic with all associated features
    :return: automatically associates some features
    """
    for feat_type in t_dic:
        for src_feat in t_dic[feat_type]:
            d = t_dic[feat_type][src_feat]
            if d is not None and is_dict(d):
                for dest_feat in d:
                    if src_feat == dest_feat:
                        t_dic[feat_type][src_feat] = dest_feat
            else:
                continue


def is_string(arg):
    string_to_test = arg
    if string_to_test is None:
        return False
    if isinstance(string_to_test, str):
        return True
    return False


def is_dict(arg):
    string_to_test = arg
    if string_to_test is None:
        return False
    if isinstance(string_to_test, dict):
        return True
    return False


def pickle_save(dic, type_c):
    file = 'textFiles/compare_feats_' + type_c
    f_pickle = open(file, "wb")
    pickle.dump(dic, f_pickle)
    f_pickle.close()
    print("progress saved")


def pickle_load(type_c):
    return olx_find_all_brands_and_models.load_brands_and_models("compare_feats_" + type_c)


def manual_associations(t_dic, type_c):
    """
    when inputting src feat value and dest feat value, dest value is always assigned and it is not checked if it
    exists or not
    :param t_dic:
    :param type_c:
    :return: changes t_dic
    """
    overwrite = False
    msg = ""
    while True:
        inp = ""
        print_associations(t_dic)
        print()
        while True:
            inp = ""
            print()
            for i in t_dic:
                print(i)
            print()
            print(msg)
            print()
            inp = input("type: 'feat_type'"
                        "or quit to quit\n"
                        "or overwrite to start overwriting\n")
            if inp == "quit":
                break
            elif inp == "overwrite":
                overwrite = not overwrite
                msg = ("overwrite is now " + str(overwrite))
                continue
            else:
                feat_type = inp
                if feat_type in t_dic:
                    break
                else:
                    feat_type = ""
                    msg = "try again"
        if inp == "quit":
            print("quitting")
            break
        msg = ""
        while True:
            inp = ""
            for i in t_dic[feat_type]:
                print()
                print("src")
                print(i)
                print()
                print("possible dests: ")
                if t_dic[feat_type][i] is None:
                    print("none")
                elif is_dict(t_dic[feat_type][i]):
                    for j in t_dic[feat_type][i]:
                        print(j)
                elif is_string(t_dic[feat_type][i]):
                    print(t_dic[feat_type][i])
            print()
            print(msg)
            print()
            inp = input("type: 'src_feat.dest_feat' (if you set 'dest_feat' equal to 'none' this means no association) "
                        "or quit to quit\n"
                        "or overwrite to start overwriting\n")
            if inp == "quit":
                msg = "previous menu"
                break
            elif inp == "overwrite":
                overwrite = not overwrite
                msg = ("overwrite is now " + str(overwrite))
                continue
            try:
                inp_list = inp.split(".")
                src = inp_list[0]
                dest = inp_list[1]

                if dest.strip().lower() == "none":
                    dest = None

                if not overwrite:
                    if is_dict(t_dic[feat_type][src]):
                        t_dic[feat_type][src] = dest
                        pickle_save(t_dic, type_c)
                        msg = "element changed"
                    else:
                        msg = "element already associated"
                        d = t_dic[feat_type][src]
                        if d is None:
                            d = "none"
                        msg = ("type " + feat_type + " source " + src + " associated to " + d)
                else:
                    t_dic[feat_type][src] = dest
                    pickle_save(t_dic, type_c)
                    msg = "element changed"
                    print()

            except IndexError:
                msg = "wrong input"
                continue


def print_associations(t_dic):
    for i in t_dic:
        print()
        print("feat type")
        print(i)

        for z in t_dic[i]:
            print()
            print("source feat: " + z)
            if is_string(t_dic[i][z]):
                print("associated with: " + t_dic[i][z])
            elif t_dic[i][z] is None:
                print("associated with: " + "none")
            else:
                print()
                print("dest feats")
                for j in t_dic[i][z]:
                    print(j)


def replace_key_dict(t_dic, type_c, feat_type, key_name, new_key_name, new_val):
    t_dic[feat_type].pop(key_name)
    t_dic[feat_type][new_key_name] = new_val
    pickle_save(t_dic, type_c)


if __name__ == "__main__":
    available_source_sites_list = ["standv", "olx"]
    available_dest_sites_list = ["volantesic"]
    print("available source sites: ")
    print(available_source_sites_list)
    print("available dest sites: ")
    print(available_dest_sites_list)

    while True:
        print("after picking, if you need to pick again you must restart tool")
        initial_inp = input("type: 'source_website'<spacebar>'dest_website' ex: standv volantesic"
                            "\n type here: ")
        initial_inp = initial_inp.split(" ")
        source_site = initial_inp[0]
        dest_site = initial_inp[1]
        if source_site not in available_source_sites_list:
            print("src_site not valid")
            continue
        if dest_site not in available_dest_sites_list:
            print("dest_site not valid")
            continue
        break

    type_comp = compare_models.get_comparison_type(source_site, dest_site)

    if len(sys.argv) > 1:
        print("args inserted")
        if "-r" in sys.argv:
            print("remaking feats")
            create_associations(type_comp)

    else:
        print("no args")
        print("starting")
        retry = False
        while True:
            try:
                comp_feats = pickle_load(type_comp)
                print("pickle loaded successfully")
            except (OSError, IOError) as e:
                print("error loading pickle")
                comp_feats = create_associations(type_comp)
            print_associations(comp_feats)
            print()
            if retry:
                print("invalid input, try again\n")
            inp = input("type 'manual' for manual association of any feat, no need to "
                        "type 'fix.feat_type.old_key.new_key.new_val' to delete a key and insert new key and value\n")
            inp = inp.lower().strip()
            if inp.startswith("manual"):
                retry = False
                manual_associations(comp_feats, type_comp)
            elif inp.startswith("fix"):
                inp_list = inp.split(".")
                feat_type = inp_list[1]
                old_key = inp_list[2]
                new_key = inp_list[3]
                new_val = inp_list[4]
                replace_key_dict(comp_feats, type_comp,feat_type, old_key, new_key, new_val)
            elif inp == "quit":
                sys.exit(0)
            else:
                retry = True
