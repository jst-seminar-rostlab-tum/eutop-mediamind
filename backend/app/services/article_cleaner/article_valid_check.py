import string


def is_article_valid(text: str) -> bool:
    """
    Check if the article text contains only allowed characters.
    This function returns True if the text is valid, meaning it does not
    contain any disallowed characters.
    """
    return not contains_disallowed_chars(text)


ALLOWED_CHARS = set(
    string.ascii_letters
    + string.digits
    + "äöüÄÖÜßéèêëàâîïôùûçÉÈÊËÀÂÎÏÔÙÛÇ"  # german, french characters
    + ".,;:!?()[]\"'-–—…"  # punctuation
    + "+-×÷=%<>±≈≠∞π√∑∆∫∂°$€£¥"  # numbers and symbols
    + "@#^&*_~|\\"
    + " "  # space
)


def contains_disallowed_chars(text: str, max_violations=5) -> bool:
    violations = 0
    for ch in text:
        if ch not in ALLOWED_CHARS and not ch.isspace():
            print(f"[Gibberish] illegal char: '{ch}' (U+{ord(ch):04X})")
            violations += 1
            if violations >= max_violations:
                print("... (too many violations, truncated)")
                return True
    return violations > 0


if __name__ == "__main__":
    test_texts = [
        "This is a normal sentence.",
        "Das ist ein normaler Satz.",
        "1234567890!@#$%^&*()_+",
        "ThisIsAVeryLongWordWithoutSpacesThatShouldBeConsideredGibberish",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        (
            "Lpolsfu tpmmfo mãoæsfyćsfhsfjgfoef Imjojtdif Qsýgvohfo "
            "fsmfjdiufsu voe hsfo{yfctsfdisfjfuoef Jogsbutsvluvsfo gýs "
            "Imjojtdif Gpstdjvoh hfg÷sefso xfsfeo/ Cftqijfmtxftjif xjse fjo "
            "esfjtfupnmjifs Njmmpjoofocusfbh {vs Wfsfgyhvoh htfufmmu gýs ejf "
            "Fjoĝyïsvoh njlspcjpncbtfjsufs M÷tvohfo- bmtp bvg Cbtjt bmmfs "
            "Pshbojtntfo- ejf {vn Cftqijm fjof Nfotdfio cftjefmo/ Bvdi tpmm "
            "FV.Hfme jo ejf FouxjdImvoh ofvfs Qspevlf gmjfâfo- ejf "
            "joevtufsjmmf Joopwbujpo wpsbosjcflo/"
        ),
        (
            "Hfqmboou jtu {vefn fjo FV.Cjpufdi.Hftfu{ - vn efo Nbslu{vhboh "
            "gýs cpjxtftodibgumjdf Fsgjoevohfo {v cftdimfvojhfo/ Ejf "
            "FV.Lpnpjttjpo xjmm bvâfsefn fjof Tdjouutufmmf pshbojtjtfo- vn "
            "Qbsousftdibgufo {xjtditfo Tubusvqt"
        ),
        "voe Jowftpuso {v wfsfjogbdifo/",
        (
            "On Wednesday, the EU Commission launched a package of measures "
            "aimed at making the EU an attractive location for life sciences. "
            'Under the umbrella term "life sciences," the EU encompasses a '
            'wide range of economic activities "that rely on knowledge about '
            'living systems," including biotechnology, agriculture, food '
            "technologies, healthcare, pharmaceuticals, medical devices, "
            "bio-based products, and biological manufacturing. According to "
            "EU estimates, these sectors employ 29 million people in Europe "
            "and generate 1.5 trillion euros. The program is to be supported "
            "annually with 10 billion euros from the EU budget. The goal is "
            "to accelerate innovations. Additionally, the trust of citizens "
            "in new technologies should be strengthened.\n\n"
            "Lpolsfu tpmnfo måoefsýcfshsfjsigfoef lmjotjdtif Qsýgvohfo "
            "fsmfjdiiufsu voe hsfo{ýcfstdisjfuoef Jogsbutsvluvsfo gýs "
            "lmjotjdtif Gpstdjvoh hfg÷sefso xfsfeo/ Cftqjfmtxftjif xjse fjo "
            "esjftufumjmfs Njmmjqpfocfusb {vs Wfsýghvoh hftufmmu gýs ejf "
            "Fjogýisvoh njlspcjpncbtfsjufs M÷tvohfo- bmtp bvg Cbtjt bmmfs "
            "Pshbojtntfo- ejf {vn Cftqjfjfm fjof Nfotdifo cftjfejfmof/ "
            "Bvdi tpmnfo FV.Hfme jo ejf Fouxjdmlvoh ofvfs Qspevlf gmjãfo- "
            "ejf joevtufsjmmf Joopwbujpo wpsbousjcflo/\n\n"
            "Hfqmboou jtu {vefn fjo FV.Cjpufdi.Hfttuf{- vn efo Nbslu{vhboh "
            "gýs cjpxtftfodbguumjdf Fsgjoevohfo {v cftdimfvojhfo/ Ejf "
            "FV.Lpnntjtjpo xjmm bãvafesfn fjof Tdiojuutufmmf pshbojtjfsfo- "
            "vn Qbsoufstdbigufo {xjtifo Tubusvqt\n\n"
            "voe Jowftupso {v wfsfjogbdifo/"
        ),
    ]
    for text in test_texts:
        print(f"Text: {text}\nIs valid: {is_article_valid(text)}\n")
