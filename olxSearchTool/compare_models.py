import sys
import pickle
import olx_find_all_brands_and_models
import volantesic_find_all_brands_and_models
import standv_find_all_brands_and_models

# GLOBAL VARS
show_already_picked = False


def log_errors(error):
    file = 'compare_errors'
    olx_find_all_brands_and_models.log_error_to_file(file, error)


def create_model_assoc(brand, src_brands_and_models, trg_brands_and_models, assoc_dic):
    olx_dest_models_dict = {}
    if brand in trg_brands_and_models.keys():
        for src_model in src_brands_and_models[brand]:
            # if list is empty (brand with no models) it just finishes this for loop TODO check if that is supposed to happen
            olx_dest_models_dict[src_model] = []
            for dest_model in trg_brands_and_models[brand]:
                olx_dest_models_dict[src_model] += [dest_model]
            assoc_dic[brand] = olx_dest_models_dict

    else:  # TODO what to do with this brands? - must be solved in car_search, with average algorithm
        error = "brand: " + brand + "\n" + "the brand does not exist in volantesic"
        log_errors(error)


def load_comparison_src_and_target(comparison_src, comparison_target):
    # TODO treat the exceptions in the except part
    src_brands_and_models = ""
    dest_brands_and_models = ""
    try:
        src_brands_and_models = comparison_src.pickle_load()
    except (OSError, IOError) as e:
        print("problem loading src in load comparison")

    try:
        dest_brands_and_models = comparison_target.pickle_load()
    except (OSError, IOError) as e:
        print("problem loading dest in load comparison")

    return src_brands_and_models, dest_brands_and_models


def load_comparison_src_and_target_by_type(type_c):
    if type_c == "olx_volantesic":
        return load_comparison_src_and_target(olx_find_all_brands_and_models, volantesic_find_all_brands_and_models)
    elif type_c == "standv_volantesic":
        return load_comparison_src_and_target(standv_find_all_brands_and_models, volantesic_find_all_brands_and_models)


def create_associations(type_c):
    src_brands_and_models, dest_brands_and_models = load_comparison_src_and_target_by_type(type_c)

    association_dict = {}  # key is olx, value is volantesic
    for brand in src_brands_and_models:
        create_model_assoc(brand, src_brands_and_models, dest_brands_and_models, association_dict)

    return association_dict


def create_and_save_associations(type_c):
    """

    :param type_c: name to save associations by
    :return: associations dictionary
    """
    assoc_dic = {}
    if type_c == "olx_volantesic":
        assoc_dic = create_associations(type_c)
    elif type_c == "standv_volantesic":
        assoc_dic = create_associations(type_c)
    else:
        print("error selecting comparison dictionaries")
        return None
    pickle_save(assoc_dic, type_c)
    return assoc_dic


def pickle_save(dic, type_c):
    file = 'textFiles/compare_struct_' + type_c
    f_pickle = open(file, "wb")
    pickle.dump(dic, f_pickle)
    f_pickle.close()
    print("progress saved")


def pickle_load(type_c):
    return olx_find_all_brands_and_models.load_brands_and_models("compare_struct_" + type_c)


def print_choices(dic, brand, model):
    print("for brand: " + brand)
    print("olx model: " + model)
    print("volantesic_model numbers: ")
    for dest_model_num in range(len(dic[brand][model])):
        volantesic_model = dic[brand][model][dest_model_num]
        if not show_already_picked:
            if is_comparison_dest_model_taken(dic, brand, volantesic_model):
                continue
            if volantesic_model in dic[brand]:
                if is_comparison_complete(dic, brand, volantesic_model):
                    continue
        print("volantesic model num: " + str(dest_model_num) + "\tvolantesic model: " + volantesic_model)


def print_brand_names(assoc_dic):
    for brand in assoc_dic:
        all_complete = True
        partial_complete = True
        done = ""

        for src_model in dic[brand]:
            if not is_comparison_complete(dic, brand, src_model):
                all_complete = False
            if not is_comparison_done_check(dic, brand, src_model):
                partial_complete = False
                break
        if all_complete:
            done = "done, all assigned"
        elif partial_complete:
            done = "done, but not all assigned"
        print(brand + "\t" + done)


def is_comparison_dest_model_taken(dic, brand, input_dest_model):
    """

    :param dic:
    :param brand:
    :param input_dest_model:
    :return: if true dest model is already taken
    """
    for src_model in dic[brand]:
        if is_comparison_complete(dic, brand, src_model):
            dest_model = dic[brand][src_model]
            if input_dest_model == dest_model:
                return True
    return False


def is_comparison_done_check(dic, brand, src_model):
    """
    :param dic:
    :param brand:
    :param model:
    :return: true if dic[brand][model] is null or a string
    """
    string_to_test = dic[brand][src_model]
    if string_to_test is None:
        return True
    if isinstance(string_to_test, str):
        return True
    return False


def is_comparison_complete(dic, brand, src_model):
    """
    :param dic:
    :param brand:
    :param model:
    :return: true if comparison is already associated with another string (src model already has dest model)
    """

    string_to_test = dic[brand][src_model]
    if string_to_test is None:
        return False
    if isinstance(string_to_test, str):
        return True
    return False


def choosing_src_dest_associations(dic, brand, type_c):
    prev_info_string = ""
    while True:
        print()
        print("olx models for: " + brand)
        for src_model in dic[brand]:
            if is_comparison_done_check(dic, brand, src_model):
                if not show_already_picked:
                    if is_comparison_complete(dic, brand, src_model):
                        continue
                    print(src_model + "\tdone")
                    continue
                else:
                    print(src_model + "\tdone")
                    continue
            print(src_model)
        print()
        print("press 'quit' to quit and save changes'")
        if prev_info_string != "":
            # info ordering
            print(prev_info_string)
            prev_info_string = ""

        src_model = input("olx model: ")
        src_model = src_model.strip().replace(" ", "-").lower()

        if src_model == "":
            prev_info_string = "invalid input"
            continue

        if src_model == "quit":
            pickle_save(dic, type_c)
            break

        if is_comparison_done_check(dic, brand, src_model):
            dest_model = "nothing, no association"
            if dic[brand][src_model] is not None:
                dest_model = dic[brand][src_model]
            prev_info_string = src_model + " is associated with: " + dest_model + "\n"
            prev_info_string += "comparison already done, must redo, try again 'quit' to quit\n"
            prev_info_string += "if there is no association, must also redo"
            continue

        if src_model in dic[brand]:
            print_choices(dic, brand, src_model)
            print("you can type 'quit' to quit or '-1' to make a model have no association")
            dest_model_num = input("dest_model_num: ")
            dest_model_num.strip().lower()

            if dest_model_num == "" or isinstance(dest_model_num, int):
                prev_info_string = "invalid input"
                continue

            if dest_model_num == "quit":
                pickle_save(dic, type_c)
                break

            try:
                dest_model_num = int(dest_model_num)
            except ValueError:
                prev_info_string = "insert a number, try again 'quit' to quit"
                continue

            if dest_model_num < -1:
                prev_info_string = "insert a valid value (-1, or > -1), try again 'quit' to quit"
                continue

            elif dest_model_num == -1:
                dic[brand][src_model] = None  # no association possible - this is correct
                continue

            elif dest_model_num >= len(dic[brand][src_model]):
                prev_info_string = "invalid volantesic model number, try again 'quit' to quit"
                continue

            dic[brand][src_model] = dic[brand][src_model][dest_model_num]
        else:
            prev_info_string = "that model doesnt exist, retype, try again 'quit' to quit"
            continue


def undo_src_dest_assoc(dic, brand_arg, type_c):
    # can create major undo and pass following 2 as args later
    src_brands_and_models, dest_brands_and_models = load_comparison_src_and_target_by_type(type_c)

    for brand in src_brands_and_models:
        if brand == brand_arg:
            create_model_assoc(brand, src_brands_and_models, dest_brands_and_models, dic)
            return
    error = "cant undo provided brand doesnt seem to exist"
    print(error)
    log_errors(error)


def auto_associations(dic):
    for brand in dic:
        for src_model in dic[brand]:
            volantesic_model_list = dic[brand][src_model]
            for dest_model_num in range(len(volantesic_model_list)):
                volantesic_model = volantesic_model_list[dest_model_num]
                if src_model == volantesic_model:
                    dic[brand][src_model] = volantesic_model


def set_association(dic, brand, src_model, dest_model):
    # sets dest to none if dest model doesnt exist
    if brand not in dic:
        return "error brand: " + brand + " doesnt exist here"
    elif src_model not in dic[brand]:
        return "model: " + src_model + " doesnt exist for brand: " + brand
    elif dest_model not in dic[brand][src_model]:
        return "dest_model: " + dest_model + " doesnt exist for model: " + src_model + " in brand: " + brand
    dic[brand][src_model] = dest_model
    return "in brand: " + brand + " associated src model: " + src_model + " to dest model: " + dest_model


def load_comparison_dic(type_c):
    """
    loads or creates a comparison dictionary based input strings
    :param src: string
    :param dest: string
    :return: comparison dict
    """

    if type_c == "standv_volantesic":
        try:
            dic = pickle_load(type_c)
            print("pickle loaded successfully")
        except (OSError, IOError) as e:
            print("error loading pickle")
            dic = create_and_save_associations(type_c)
    elif type_c == "olx_volantesic":
        try:
            dic = pickle_load(type_c)
            print("pickle loaded successfully")
        except (OSError, IOError) as e:
            print("error loading pickle")
            dic = create_and_save_associations(type_c)
    else:
        error = "type doesnt exist"
        print(error)
        log_errors(error)
    return dic


def get_comparison_type(src, dest):
    if src == "standv" and dest == "volantesic":
        return "standv_volantesic"
    elif src == "olx" and dest == "volantesic":
        return "olx_volantesic"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("arguments found")
        if len(sys.argv) == 2:
            if "-h" in sys.argv:
                print("-h for help")
                print("-r to remake associations dict")
                print("no arguments to start where u left of")

            else:
                print("invalid args")
                print("-h for help")
                print("-r filename to remake everything")
                print("no arguments to start where u left of")
        elif len(sys.argv) == 3:
            if "-r" == sys.argv[1]:
                type_compare = sys.argv[2]
                print("remaking associations dict")
                create_and_save_associations(type_compare)
            else:
                print("invalid args")
        else:
            print("invalid args")

    else:
        print("starting")
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

        type_comp = get_comparison_type(source_site, dest_site)
        dic = load_comparison_dic(type_comp)
        auto_associations(dic)

        retry = False
        message = ""
        while True:
            print_brand_names(dic)
            print()
            if retry:
                print("invalid input, try again\n")
            print(message)
            message = ""
            inp = input(
                "type 'quit' to quit (everytime you quit progress is saved), type 'brand_name' to start association,"
                "\n type 'redo<space>brand_name' to redo (redo will delete all in brand) "
                "afterwards\n type restart to restart everything after automatic associations are applied\n"
                "type 'manual brand src_model volantesic_model' for manual association of any given model, no need to "
                "redo (if you set'volantesic_model' equal to 'none' this means no association): \n"
                "type: 'hide_picked' to hide all brands with a match 'show_picked' to show all brands\n"
                "type: 'auto' to auto complete all no associations (assigns all it cans with -1)\n"
                ""
                "\ntype here: ")
            print()
            inp = inp.lower().strip().replace(" ", "-")

            if inp in dic:
                retry = False
                brand = inp
                choosing_src_dest_associations(dic, brand, type_comp)
                pickle_save(dic, type_comp)

            elif inp.startswith("redo"):
                # will delete all in brand and redirect you to the brand to do everything all over again
                retry = False
                inp_list = inp.split("-")
                arg_brand = inp_list[1]
                undo_src_dest_assoc(dic, arg_brand, type_comp)
                auto_associations(dic)
                choosing_src_dest_associations(dic, arg_brand, type_comp)
                pickle_save(dic, type_comp)

            elif inp == "restart":
                retry = False
                dic = create_and_save_associations(type_comp)
                auto_associations(dic)
                pickle_save(dic, type_comp)

            elif inp.startswith("manual"):
                retry = False
                inp_list = inp.split("-")
                arg_brand = inp_list[1]
                arg_model_src = inp_list[2]  # ex: model from standv
                arg_model_dest = inp_list[3]  # ex: model from volantesic
                if arg_model_dest.strip().lower() == "none":
                    arg_model_dest = None
                message = set_association(dic, arg_brand, arg_model_src, arg_model_dest)
                pickle_save(dic, type_comp)

            elif inp == "quit":
                pickle_save(dic, type_comp)
                exit(0)

            elif inp == "hide_picked":
                retry = False
                show_already_picked = False
                message = "hiding all brands already associated"

            elif inp == "show_picked":
                retry = False
                show_already_picked = True
                message = "showing all brands"

            elif inp == "auto":
                # TODO autocomplete all source models that cant be compared anymore
                message = "auto completing"
            else:
                retry = True

# TODO must be possible to compare a source with several destinations, example: compare standvirtual with volantesic
#  and then kbb or vice versa
