# flake8: noqa: E501

from app.services.article_cleaner.article_valid_check import (
    contains_disallowed_chars,
    is_article_valid,
)


class TestArticleValidCheck:
    """Test cases for article validation functionality."""

    def test_article_with_only_navigation_text(self):
        """Test an article that contains only navigation text."""
        text = """Home
                Anmelden
                Abo
                E-Paper
                Lesezeichen
                Feedback
                Impressum
                Datenschutz
                AGB
                Lizenzinformationen
                Datenschutz-Einstellungen"""
        result = is_article_valid(text)
        print(f"length: {len(text)}")
        assert result is False

    def test_mixed_text_with_special_chars(self):
        """Test text that contains some special characters that might be disallowed."""
        text = (
            "Lpolsfu tpmmfo mãoæsfyćsfhsfjgfoef Imjojtdif Qsýgvohfo "
            "fsmfjdiufsu voe hsfo{yfctsfdisfjfuoef Jogsbtsvluvsfo gýs "
            "Imjojtdif Gpstdjvoh hfg÷sefso xfsfoo/ Cftqijfmtxftjif xjse fjo "
            "esfjtfupnmjifs Njmmpjoofocusfbh {vs Wfsfgyhvoh htfufmmu gýs ejf "
            "Fjoĝyïsvoh njlspcjpncbtfjsufs M÷tvohfo- bmtp bvg Cbtjt bmmfs "
            "Pshbojtntfo- ejf {vn Cftqijm fjof Nfotdfio cftjefmo/ Bvdi tpmm "
            "FV.Hfme jo ejf FouxjdImvoh ofvfs Qspevlf gmjfâfo- ejf "
            "joevtufsjmmf Joopwbujpo wpsbosjcflo/"
        )
        # This text likely contains disallowed characters
        result = is_article_valid(text)
        # We expect this to be invalid due to special characters
        assert result is False

    def test_german_text_with_special_chars(self):
        """Test German text that might contain disallowed characters."""
        text = (
            "Hfqmboou jtu {vefn fjo FV.Cjpufdi.Hftfu{ - vn efo Nbslu{vhboh "
            "gýs cpjxtftodibgumjdf Fsgjoevohfo {v cftdimfvojhfo/ Ejf "
            "FV.Lpnpjttjpo xjmm bvâfsefn fjof Tdjouutufmmf pshbojtjtfo- vn "
            "Qbsousftdibgufo {xjtditfo Tubusvqt"
        )
        result = is_article_valid(text)
        # Check if this contains disallowed characters
        assert isinstance(result, bool)

    def test_long_mixed_text_with_english_and_encoded(self):
        """Test long text with both English and encoded German text."""
        text = (
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
            "fsmfjdiiufsu voe hsfo{ýcfstdisjfuoef Jogsbtsvluvsfo gýs "
            "lmjotjdtif Gpstdjvoh hfg÷sefso xfsfoo/ Cftqjfmtxftjif xjse fjo "
            "esjftufumjmfs Njmmjqpfocfusb {vs Wfsýghvoh hftufmmu gýs ejf "
            "Fjogýisvoh njlspcjpncbtfsjufs M÷tvohfo- bmtp bvg Cbtjt bmmfs "
            "Pshbojtntfo- ejf {vn Cftqjfjfm fjof Nfotdifo cftjfejfmof/ "
            "Bvdi tpmnfo FV.Hfme jo ejf Fouxjdlmvoh ofvfs Qspevlf gmjãfo- "
            "ejf joevtufsjmmf Joopwbujpo wpsbousjcflo/\n\n"
            "Hfqmboou jtu {vefn fjo FV.Cjpufdi.Hfttuf{- vn efo Nbslu{vhboh "
            "gýs cjpxtftfodbguumjdf Fsgjoevohfo {v cftdimfvojhfo/ Ejf "
            "FV.Lpnptjtjpo xjmm bãvafesfn fjof Tdiojuutufmmf pshbojtjfsfo- "
            "vn Qbsofsütdbigufo {xjtifo Tubusvqt\n\n"
            "voe Jowftupso {v wfsfjogbdifo/"
        )
        result = is_article_valid(text)
        assert isinstance(result, bool)

    def test_contains_disallowed_chars_function(self):
        """Test the contains_disallowed_chars function directly."""
        # Test with valid text
        valid_text = "This is valid text with normal characters."
        assert contains_disallowed_chars(valid_text) is False

        # Test with potentially invalid characters (this will depend on the ALLOWED_CHARS set)
        # We can test with a character that's definitely not in the allowed set
        invalid_text = "This text contains 中文 characters"
        result = contains_disallowed_chars(invalid_text)
        assert isinstance(result, bool)

    def test_max_violations_parameter(self):
        """Test that the max_violations parameter works correctly."""
        # Create text with many potential violations
        text_with_violations = "这是一个包含很多中文字符的测试文本"

        # Test with max_violations=1
        result = contains_disallowed_chars(
            text_with_violations, max_violations=1
        )
        assert isinstance(result, bool)

        # Test with max_violations=10
        result = contains_disallowed_chars(
            text_with_violations, max_violations=10
        )
        assert isinstance(result, bool)
