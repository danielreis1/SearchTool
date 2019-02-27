import sys
import pickle
import olx_find_all_brands_and_models
import volantesic_find_all_brands_and_models


def log_errors(error):
    file = 'compare_errors'
    olx_find_all_brands_and_models.log_error_to_file(file, error)


def create_model_assoc(brand, src_brands_and_models, trg_brands_and_models, assoc_dic):
    olx_volante_models_dict = {}
    if brand in trg_brands_and_models.keys():
        for olx_model in src_brands_and_models[brand]:
            # if list is empty (brand with no models) it just finishes this for loop TODO check if that is supposed to
            olx_volante_models_dict[olx_model] = []
            for volante_model in trg_brands_and_models[brand]:
                olx_volante_models_dict[olx_model] += [volante_model]
            assoc_dic[brand] = olx_volante_models_dict

    else:
        error = "brand: " + brand + "\n" + "the brand does not exist in volantesic"
        log_errors(error)


def load_comparison_src_and_target(comparison_src, comparison_target):
    # TODO surround the following with 2 != try catches and create the brand_model dictionaries if required
    src_brands_and_models = ""
    dest_brands_and_models = ""
    try:
        src_brands_and_models = comparison_target.pickle_load()
    except:
        print("problem loading dest in load comparison")

    try:
        dest_brands_and_models = comparison_src.pickle_load()
    except:
        print("problem loading dest in load comparison")

    return src_brands_and_models, dest_brands_and_models


def create_associations(comparison_src, comparison_target):
    src_brands_and_models, dest_brands_and_models = load_comparison_src_and_target(comparison_src, comparison_target)

    association_dict = {}  # key is olx, value is volantesic
    for brand in src_brands_and_models:
        create_model_assoc(brand, src_brands_and_models, dest_brands_and_models, association_dict)

    return association_dict


def create_olx_volantesic_assoc():
    assoc_dic = create_associations(volantesic_find_all_brands_and_models, olx_find_all_brands_and_models)
    pickle_save(assoc_dic, 'olx_volantesic')
    return assoc_dic


def olx_volante_pickle_save(assoc_dic):
    pickle_save(assoc_dic, 'olx_volantesic')


def pickle_save(dic, type):
    file = 'textFiles/compare_struct_' + type
    f_pickle = open(file, "wb")
    pickle.dump(dic, f_pickle)
    f_pickle.close()


def pickle_load(type):
    return olx_find_all_brands_and_models.load_brands_and_models("compare_struct_" + type)


def pickle_load_olx_volante():
    return pickle_load("olx_volantesic")


def print_choices(dic, brand, model):
    print("for brand: " + brand)
    print("olx model: " + model)
    print("volantesic_model numbers: ")
    for volantesic_model_num in range(len(dic[brand][model])):
        volantesic_model = dic[brand][model][volantesic_model_num]
        print("volantesic model num: " + str(volantesic_model_num) + "\tvolantesic model: " + volantesic_model)


def print_brand_names(assoc_dic):
    for brand in assoc_dic:
        print(brand)


def is_comparison_done_check(dic, brand, model):
    """
    :param dic:
    :param brand:
    :param model:
    :return: true if dic[brand][model] is null or a string
    """
    string_to_test = dic[brand][model]
    if string_to_test is None:
        return True
    if isinstance(string_to_test, str):
        return True
    return False


def choosing_olx_volantesic(dic, brand):
    prev_info_string = ""
    while True:

        print()
        print("olx models for: " + brand)
        for olx_model in dic[brand]:
            if is_comparison_done_check(dic, brand, olx_model):
                print(olx_model + "\tdone")
                continue
            print(olx_model)
        print()
        print("press 'quit' to quit and save changes'")
        if prev_info_string != "":
            # info ordering
            print(prev_info_string)
            prev_info_string = ""

        olx_model = input("olx model: ")
        olx_model = olx_model.strip().replace(" ", "-").lower()

        if olx_model == "":
            prev_info_string = "invalid input"
            continue

        if olx_model == "quit":
            olx_volante_pickle_save(dic)
            break

        if is_comparison_done_check(dic, brand, olx_model):
            volante_model = "nothing, no association"
            if dic[brand][olx_model] is not None:
                volante_model = dic[brand][olx_model]
            prev_info_string = olx_model + " is associated with: " + volante_model + "\n"
            prev_info_string += "comparison already done, must redo, try again 'quit' to quit\n"
            prev_info_string += "if there is no association, must also redo"
            continue

        if olx_model in dic[brand]:
            print_choices(dic, brand, olx_model)
            volantesic_model_num = input("volantesic_model_num: ")
            volantesic_model_num.strip().lower()

            if volantesic_model_num == "" or isinstance(volantesic_model_num, int):
                prev_info_string = "invalid input"
                continue

            if volantesic_model_num == "quit":
                olx_volante_pickle_save(dic)
                break

            try:
                volantesic_model_num = int(volantesic_model_num)
            except ValueError:
                prev_info_string = "insert a number, try again 'quit' to quit"
                continue

            if volantesic_model_num < -1:
                prev_info_string = "insert a valid value (-1, or > -1), try again 'quit' to quit"
                continue

            elif volantesic_model_num == -1:
                dic[brand][olx_model] = None  # no association possible - this is correct
                continue

            elif volantesic_model_num >= len(dic[brand][olx_model]):
                prev_info_string = "invalid volantesic model number, try again 'quit' to quit"
                continue

            dic[brand][olx_model] = dic[brand][olx_model][volantesic_model_num]
        else:
            prev_info_string = "that model doesnt exist, retype, try again 'quit' to quit"
            continue


def undo_olx_volante_assoc(dic, brand_arg):
    # can create major undo and pass following 2 as args later
    volante_brands_and_models = volantesic_find_all_brands_and_models.pickle_load()
    olx_brands_and_models = olx_find_all_brands_and_models.pickle_load()

    for brand in olx_brands_and_models:
        if brand == brand_arg:
            create_model_assoc(brand, olx_brands_and_models, volante_brands_and_models, dic)
            return
    error = "cant undo provided brand doesnt seem to exist"
    print(error)
    log_errors(error)


def auto_associations(dic):
    for brand in dic:
        for olx_model in dic[brand]:
            volantesic_model_list = dic[brand][olx_model]
            for volantesic_model_num in range(len(volantesic_model_list)):
                volantesic_model = volantesic_model_list[volantesic_model_num]
                if olx_model == volantesic_model:
                    dic[brand][olx_model] = volantesic_model


def set_association(dic, brand, src_model, dest_model):
    # sets dest to none if dest model doesnt exist
    if brand not in dic:
        return "error brand: " + brand + " doesnt exist here"
    elif src_model not in dic[brand]:
        return "model: " + src_model + " doesnt exist for brand: " + brand
    elif dest_model not in dic[brand][src_model]:
        return "dest_model: " + dest_model + " doesnt exist for model: " + src_model + " in brand: " + brand
    dic[brand][src_model] = dest_model
    return "in brand: " + brand + " associated olx: " + src_model + " to volantesic: " + dest_model


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("arguments found")
        if len(sys.argv) == 2:
            if "-h" in sys.argv:
                print("-h for help")
                print("-r to remake associations dict")
                print("no arguments to start where u left of")
            elif "-r":
                print("remaking associations dict")
                create_olx_volantesic_assoc()
        print("not a valid command")
        print("-h for help")
        print("-r to remake everything")
        print("no arguments to start where u left of")

    else:
        print("starting")
        dic = {}
        try:
            print("pickle loaded successfully")
            dic = pickle_load_olx_volante()
        except (OSError, IOError) as e:
            print("error loading pickle")
            dic = create_olx_volantesic_assoc()

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
                "type 'manual brand olx_model volantesic_model' for manual association of any given model, no need to "
                "redo (if you set'volantesic_model' equal to 'none' this means no association): \ntype here: ")
            print()
            inp = inp.lower().strip().replace(" ", "-")

            if inp in dic:
                retry = False
                brand = inp
                choosing_olx_volantesic(dic, brand)
                olx_volante_pickle_save(dic)
                message = "success, progress saved"

            elif inp.startswith("redo"):
                # will delete all in brand and redirect you to the brand to do everything all over again
                retry = False
                inp_list = inp.split("-")
                arg_brand = inp_list[1]
                undo_olx_volante_assoc(dic, arg_brand)
                auto_associations(dic)
                choosing_olx_volantesic(dic, arg_brand)
                olx_volante_pickle_save(dic)
                message = "success, progress saved"

            elif inp == "restart":
                dic = create_olx_volantesic_assoc()
                auto_associations(dic)
                olx_volante_pickle_save(dic)
                message = "success, progress saved"

            elif inp.startswith("manual"):
                inp_list = inp.split("-")
                arg_brand = inp_list[1]
                arg_model_src = inp_list[2]  # olx
                arg_model_dest = inp_list[3]  # volantesic
                if arg_model_dest.strip().lower() == "none":
                    arg_model_dest = None
                messg = set_association(dic, arg_brand, arg_model_src, arg_model_dest)
                message = "success, progress saved \n" + messg

            elif inp == "quit":
                olx_volante_pickle_save(dic)
                message = "success, progress saved"
                exit(0)

            else:
                retry = True
