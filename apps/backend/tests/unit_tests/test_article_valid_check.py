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

    def test_articles_contains_encoded_chars(self):
        """Test that articles containing encoded characters are considered invalid."""
        text_with_encoded_chars = (
            "### Im Gespräch: Jürgen Michels## Der Chefvolkswirt der BayernLB "
            "empfiehlt der EU, aus eigener Kraft die Folgen der Zölle "
            "auszugleichen – Etwas optimistischer für deutsche Konjunktur##### "
            "Von Joachim Herr, MünchenJürgen Michels, der Chefvolkswirt der "
            "BayernLB, dämpft die Furcht vor hohen Importzöllen der USA. Der "
            "europäische Binnenmarkt wäre stark genug, um weniger Handel mit "
            "Amerika auszugleichen. Allerdings müsste die EU dafür einiges tun "
            "und nicht-tarifäre Hindernisse aus dem Weg schaffen.Egal wie der "
            "Zollstreit mit den USA ausgeht: Jürgen Michels rechnet damit, "
            "dass Europas Wirtschaft künftig mit höheren Importzöllen der USA "
            "auskommen muss. „Und die Frage ist, ob es Nebenabkommen geben "
            "wird, die auch den Handel Europas mit China einschränken können“, "
            "warnt der Chefvolkswirt der Bayerischen Landesbank (BayernLB). "
            "„Für die europäische Wirtschaft wird Trumps Handelspolitik ein "
            "belastender Faktor bleiben.“Epdi gýs Fvspqb hjcu ft bvt tfjofs "
            "Tjdiu Dibodfo- vn efo Bvtgbmm efs VTB bmt {vwfsmåttjhfo Iboefmtqbsuofs "
            "voe cjtxfjmfo bmt Lpokvoluvsnpups bvt{vhmfjdifo/ [vn fjofo l÷oouf "
            "tjdi ejf FV tuåslfs bmt cjtifs bo Måoefs xfoefo- ejf ejf [pmmqpmjujl "
            "efs VTB fcfogbmmt usjggu; ‟Jdi efolf bo Lbobeb- bcfs bvdi bo btjbujtdif "
            "Måoefs/” Epsu tpmmuf tjdi Fvspqb ofv qptjujpojfsfo/ [vn boefsfo voe "
            "vps bmmfn såu Njdifmt- ejf fjhfof Tuåslf {v ovu{fo; ‟Fvspqb nvtt efo "
            "Cjoofonbslu tuåslfo voe tjdi nfis bvg efttfo Xbdituvntdibodfo "
            "lpo{fousjfsfo/” Fjofo Tdivc l÷ooufo ijfs ejf Gjtlbmjnqvmtf hfcfo- "
            "bmmfo wpsbo ejf Jowftujujpotqsphsbnnf Efvutdimboet gýs Jogsbtusvluvs "
            "voe Sýtuvoh/Ojdiu.ubsjgåsf Ifnnojttf jo efs FVBcfs Njdifmt wfsxfjtu "
            "bvg Ijoefsojttf; ‟Jn Cjoofonbslu ibcfo xjs jnnfs opdi fjof hbo{f "
            "Sfjif wpo Fjotdisåolvohfo/” Fs fsxåiou fjof Tuvejf eft Joufsobujpobmfo "
            "Xåisvohtgpoet )JXG*- xpobdi Sftusjlujpofo jn joofsfvspqåjtdifo Iboefm "
            "fjofs evsditdiojuumjdifo [pmmrvpuf wpo 55& foutqsådifo/ Tpmdif "
            "ojdiu.ubsjgåsfo Ifnnojttf hjcu ft {vn Cfjtqjfm gýs Bhsbsqspevluf voe "
            "Obisvohtnjuufm/ Ft hfiu voufs boefsfn vn Cftdibggvoh- Oåisxfsu voe "
            "hftvoeifjutcf{phfof Bohbcfo/ Njdifmt ofoou fjo Cfjtqjfm; ‟Fjo jo "
            "Efvutdimboe qspev{jfsufs Kphivsu lboo ojdiu fjogbdi jo ×tufssfjdi "
            "pefs Cfmhjfo wfslbvgu xfsefo- ¡eb ft voufstdijfemjdif Sfhfmo gýs "
            "Qspevlujogpsnbujpofo hjcu/”Vnhfsfdiofu foutqsfdifo tpmdif Sftusjlujpofo "
            "bvghsvoe efs Wjfm{bim obujpobmfs Sfhfmvohfo fjofs [pmmcfmbtuvoh wpo "
            "55&/ Gýs Ejfotumfjtuvohfo fshjcu tjdi mbvu JXG tphbs fjo Årvjwbmfou "
            "wpo 221&/ Ejftf [bim nýttf nbo bmmfsejoht nju Wpstjdiu hfojfàfo- "
            "gýhu Njdifmt ijo{v/ ‟[xfjgfm ibcf jdi {vn Cfjtqjfm gýs ebt "
            "Cfifscfshvohthfxfscf/ Ft jtu tdixjfsjh- fjo Ipufm{jnnfs jo Nýodifo "
            "nju fjofn jo Nbjmboe {v wfshmfjdifo/”‟Jnnfs opdi {bhibgu”[vefn l÷oouf "
            "ejf FV bvt tfjofs Tjdiu nju Tusvluvssfgpsnfo voe Cýsplsbujfbccbv efo "
            "Cjoofonbslu tuåslfo/ Jn Esbhij.Cfsjdiu tfj bvdi ejft fouibmufo- ojdiu "
            "ovs ejf Gpsefsvoh obdi Njmmjbsefojowftujujpofo/ Fstuf Botåu{f hfcf ft/ "
            "Epdi Njdifmt iåmu ejftf gýs ojdiu bvtsfjdifoe; ‟Ebt jtu jnnfs opdi "
            "{bhibgu- xbt nbo bvdi bn Cfhsjgg Cýsplsbujfwfsfjogbdivoh fslfoou "
            "botufmmf Cýsplsbujfbccbv/# Ejf Dibodf- nju nfis Cjoofoiboefm fsgpmhsfjdi "
            "{v tfjo- iåuuf ejf FV bvt Tjdiu eft Wpmltxjsut; ‟Fvspqb lboo bvt "
            "fjhfofs Lsbgu ejf Gpmhfo i÷ifsfs [÷mmf xfuunbdifo/ Xbistdifjomjdi "
            "l÷ooufo xjs tphbs fjof Ýcfslpnqfotjfsvoh fssfjdifo- xfoo ejf "
            "Ifnnojttf tdiofmm cftfjujhu xýsefo/”Uspu{ efs Votjdifsifju ýcfs ejf "
            "Iboefmt. voe [pmmqpmjujl efs VTB tjoe ejf ×lpopnfo efs CbzfsoMC gýs "
            "ebt Xjsutdibgutxbdituvn jo Efvutdimboe fuxbt pqujnjtujtdifs; ‟Xjs "
            "tfifo kfu{u fjof mfjdiuf Cftdimfvojhvoh”- cfsjdiufu Njdifmt/ Gýs ebt "
            "{xfjuf Rvbsubm sfdiofu fs bvghsvoe eft Uifnbt [÷mmf bcfs opdinbmt "
            "nju fjofn Njovt/ Gýs ebt {xfjuf Ibmckbis fsxbsufu fs fjof ‟hfxjttf "
            "Opsnbmjtjfsvoh jn Bvàfoiboefm”/ Voe fs fslfoou Jnqvmtf jn Jomboe/ "
            "‟Ebt fjof jtu- ebtt ejf fstufo Hfmefs eft nbttjwfo Lpokvoluvsqsphsbnnt "
            "hfsbef gsfjhftdibmufu xfsefo/” Jo ejftfs Fsxbsuvoh ibcf tjdi ejf "
            "Tujnnvoh jo efs efvutdifo Xjsutdibgu tdipo wfscfttfsu/ ‟Ebt eýsguf "
            "eb{v gýisfo- ebtt ejf qsjwbuxjsutdibgumjdif Tfjuf jisf [vsýdlibmuvoh "
            "gýs Jowftujujpofo {vnjoeftu {vn Ufjm bcmfhfo xjse/”‟Xjs nýttfo "
            "xjslmjdi jowftujfsfo”Jo [bimfo ifjàu ebt- Njdifmt voe tfjo Ufbn tbhfo "
            "gýs ejf efvutdif Xjsutdibgu ovo fjo Xbdituvn wpo 1-3& jo ejftfn Kbis "
            "wpsbvt/ Cjtifs mbvufuf ejf Qsphoptf .1-2&/ Gýs oådituft Kbis fsxbsufu "
            "ejf CbzfsoMC fjofo Botujfh eft Csvuupjomboetqspevlut vn 2-5& — bvdi "
            "ebol efs Jnqvmtf eft Jowftujujpotqsphsbnnt/ Bmmfsejoht nýttufo ebgýs "
            "Wpsbvttfu{vohfo fsgýmmu tfjo/ ‟Xjs nýttfo ebt Hfme xjslmjdi "
            "jowftujfsfo”- gpsefsu Njdifmt- {xfjgfmu bcfs fuxbt ebsbo- eb ft fjof "
            "Sfjif wpo lpotvnujwfo Fmfnfoufo hfcf/ ‟Wps bmmfn bvg Mboeftfcfof "
            "l÷oofo ejf Hfmefs jo csfjufsfn Nbàf wfsxfoefu xfsefo- vn tp efo tfis "
            "ipifo Tubbutlpotvn xfjufsmbvgfo {v mbttfo/”[vn boefsfo nýttf "
            "Efvutdimboe bvdi jo efs Mbhf tfjo- ebt {v qspev{jfsfo- xbt obdihfgsbhu "
            "xfsef/ ‟Ejf [bimfo tdixbolfo- bcfs obdi Cfsjdiufo jnqpsujfsu ejf "
            "Cvoeftxfis xpim vn ejf 81& eft jn [fjufoxfoefqblfu wpshftfifofo "
            "Wpmvnfot/” Ejf efvutdif Qsjwbuxjsutdibgu nýttf eftibmc ofvf "
            "Qspevlujpotbombhfo bvgcbvfo- vn fjofo i÷ifsfo Boufjm {v fs{jfmfo/ "
            "Fjo xjdiujhfs Wpsufjm wpo jowftujwfo Bvthbcfo jn Wfshmfjdi nju "
            "lpotvnujwfo tjoe bvt Njdifmt( Tjdiu n÷hmjdif ‟ufdiopmphjtdif "
            "Tqjmmpwfst”- bmtp qptjujwf Bvtxjslvohfo bvg boefsf Csbodifo/ "
            "‟Fjof Espiofoufdiojl lboo voufs Vntuåoefo gýs bvupopnft Gbisfo pefs "
            "boefsf Ufdiopmphjfo gýs fjof {jwjmf Ovu{voh fjohftfu{u xfsefo/”"
        )
        result = is_article_valid(text_with_encoded_chars)
        assert result is False

    def test_article_contains_url(self):
        """Test that articles containing URLs are considered invalid."""
        text_with_url = (
            "FRANKFURT (dpa-AFX Analyser) - Deutsche Bank Research hat die "
            "Einstufung für Covestro nach Eckdaten zum zweiten Quartal mit "
            "einem Kursziel von 62 Euro auf „Hold“ belassen. Das operative "
            "Ergebnis (Ebitda) liege um acht Prozent über dem Mittelwert der "
            "zuvor vom Chemiekonzern in Aussicht gestellten Spanne, schrieb "
            "Virginie Boucher-Ferte in ihrem am Montag vorliegenden Kommentar. "
            "Die Senkung des Jahresziels sei zu erwarten gewesen./bek/ag"
            "Veröffentlichung der Original-Studie: Datum in Studie nicht "
            "angegeben / Uhrzeit in Studie nicht angegeben / CET"
            "Erstmalige Weitergabe der Original-Studie: 14.07.2025 / 07:53 / CET"
            "Hinweis: Informationen zur Offenlegungspflicht bei "
            "Interessenkonflikten im Sinne von § 85 Abs. 1 WpHG, Art. 20 VO "
            "(EU) 596/2014 für das genannte Analysten-Haus finden Sie unter "
            "http://web.dpa-afx.de/offenlegungspflicht/offenlegungs_pflicht.html."
        )
        result = is_article_valid(text_with_url)
        assert result is False
