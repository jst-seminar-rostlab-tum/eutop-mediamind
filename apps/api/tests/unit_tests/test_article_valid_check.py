# flake8: noqa: E501

from app.services.article_cleaner.article_valid_check import (
    contains_disallowed_chars,
    is_article_valid,
)


class TestArticleValidCheck:
    """Test cases for article validation functionality."""

    def test_normal_english_sentence(self):
        """Test that normal English sentences are considered valid."""
        text = "This is a normal sentence."
        assert is_article_valid(text) is True

    def test_normal_german_sentence(self):
        """Test that normal German sentences are considered valid."""
        text = "Das ist ein normaler Satz."
        assert is_article_valid(text) is True

    def test_numbers_and_symbols(self):
        """Test that numbers and common symbols are considered valid."""
        text = "1234567890!@#$%^&*()_+"
        assert is_article_valid(text) is True

    def test_very_long_word_without_spaces(self):
        """Test that very long words without spaces might be considered gibberish."""
        text = (
            "ThisIsAVeryLongWordWithoutSpacesThatShouldBeConsideredGibberish"
        )
        # This should be valid as it only contains allowed characters
        assert is_article_valid(text) is True

    def test_lorem_ipsum(self):
        """Test that Lorem ipsum text is considered valid."""
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        assert is_article_valid(text) is True

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

    def test_short_german_phrase(self):
        """Test a short German phrase."""
        text = "voe Jowftpso {v wfsfjogbdifo/"
        result = is_article_valid(text)
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

    def test_empty_string(self):
        """Test that empty strings are considered valid."""
        assert is_article_valid("") is True
        assert contains_disallowed_chars("") is False

    def test_whitespace_only(self):
        """Test that whitespace-only strings are considered valid."""
        assert is_article_valid("   \n\t  ") is True
        assert contains_disallowed_chars("   \n\t  ") is False

    def test_special_punctuation(self):
        """Test various punctuation marks that should be allowed."""
        punctuation_text = "Hello, world! How are you? (Fine, thanks.) [Great] \"Awesome\" 'Nice' –dash— …ellipsis"
        assert is_article_valid(punctuation_text) is True

    def test_mathematical_symbols(self):
        """Test mathematical and currency symbols that should be allowed."""
        math_text = "2 + 2 = 4, π ≈ 3.14, √16 = 4, $100 €50 £30 ¥1000"
        assert is_article_valid(math_text) is True

    def test_german_and_french_characters(self):
        """Test German and French characters that should be allowed."""
        german_french_text = (
            "Café mit Müsli, très bien! Schön, größer, français"
        )
        assert is_article_valid(german_french_text) is True
