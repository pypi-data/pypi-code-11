# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateNumbers, RSAPublicNumbers
)


RSA_KEY_512 = RSAPrivateNumbers(
    p=int(
        "d57846898d5c0de249c08467586cb458fa9bc417cdf297f73cfc52281b787cd9", 16
    ),
    q=int(
        "d10f71229e87e010eb363db6a85fd07df72d985b73c42786191f2ce9134afb2d", 16
    ),
    d=int(
        "272869352cacf9c866c4e107acc95d4c608ca91460a93d28588d51cfccc07f449"
        "18bbe7660f9f16adc2b4ed36ca310ef3d63b79bd447456e3505736a45a6ed21", 16
    ),
    dmp1=int(
        "addff2ec7564c6b64bc670d250b6f24b0b8db6b2810099813b7e7658cecf5c39", 16
    ),
    dmq1=int(
        "463ae9c6b77aedcac1397781e50e4afc060d4b216dc2778494ebe42a6850c81", 16
    ),
    iqmp=int(
        "54deef8548f65cad1d411527a32dcb8e712d3e128e4e0ff118663fae82a758f4", 16
    ),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "ae5411f963c50e3267fafcf76381c8b1e5f7b741fdb2a544bcf48bd607b10c991"
            "90caeb8011dc22cf83d921da55ec32bd05cac3ee02ca5e1dbef93952850b525",
            16
        ),
    )
)

RSA_KEY_512_ALT = RSAPrivateNumbers(
    p=int(
        "febe19c29a0b50fefa4f7b1832f84df1caf9be8242da25c9d689e18226e67ce5",
        16),
    q=int(
        "eb616c639dd999feda26517e1c77b6878f363fe828c4e6670ec1787f28b1e731",
        16),
    d=int(
        "80edecfde704a806445a4cc782b85d3f36f17558f385654ea767f006470fdfcbda5e2"
        "206839289d3f419b4e4fb8e1acee1b4fb9c591f69b64ec83937f5829241", 16),
    dmp1=int(
        "7f4fa06e2a3077a54691cc5216bf13ad40a4b9fa3dd0ea4bca259487484baea5",
        16),
    dmq1=int(
        "35eaa70d5a8711c352ed1c15ab27b0e3f46614d575214535ae279b166597fac1",
        16),
    iqmp=int(
        "cc1f272de6846851ec80cb89a02dbac78f44b47bc08f53b67b4651a3acde8b19",
        16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "ea397388b999ef0f7e7416fa000367efd9a0ba0deddd3f8160d1c36d62267f210"
            "fbd9c97abeb6654450ff03e7601b8caa6c6f4cba18f0b52c179d17e8f258ad5",
            16),
    )
)

RSA_KEY_522 = RSAPrivateNumbers(
    p=int(
        "1a8aab9a069f92b52fdf05824f2846223dc27adfc806716a247a77d4c36885e4bf",
        16),
    q=int(
        "19e8d620d177ec54cdb733bb1915e72ef644b1202b889ceb524613efa49c07eb4f",
        16),
    d=int(
        "10b8a7c0a92c1ae2d678097d69db3bfa966b541fb857468291d48d1b52397ea2bac0d"
        "4370c159015c7219e3806a01bbafaffdd46f86e3da1e2d1fe80a0369ccd745", 16),
    dmp1=int(
        "3eb6277f66e6e2dcf89f1b8529431f730839dbd9a3e49555159bc8470eee886e5",
        16),
    dmq1=int(
        "184b4d74aa54c361e51eb23fee4eae5e4786b37b11b6e0447af9c0b9c4e4953c5b",
        16),
    iqmp=int(
        "f80e9ab4fa7b35d0d232ef51c4736d1f2dcf2c7b1dd8716211b1bf1337e74f8ae",
        16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "2afaea0e0bb6fca037da7d190b5270a6c665bc18e7a456f7e69beaac4433db748"
            "ba99acdd14697e453bca596eb35b47f2d48f1f85ef08ce5109dad557a9cf85ebf"
            "1", 16),
    ),
)

RSA_KEY_599 = RSAPrivateNumbers(
    p=int(
        "cf95d20be0c7af69f4b3d909f65d858c26d1a7ef34da8e3977f4fa230580e58814b54"
        "24be99", 16),
    q=int(
        "6052be4b28debd4265fe12ace5aa4a0c4eb8d63ff8853c66824b35622161eb48a3bc8"
        "c3ada5", 16),
    d=int(
        "69d9adc465e61585d3142d7cc8dd30605e8d1cbbf31009bc2cd5538dc40528d5d68ee"
        "fe6a42d23674b6ec76e192351bf368c8968f0392110bf1c2825dbcff071270b80adcc"
        "fa1d19d00a1", 16),
    dmp1=int(
        "a86d10edde456687fba968b1f298d2e07226adb1221b2a466a93f3d83280f0bb46c20"
        "2b6811", 16),
    dmq1=int(
        "40d570e08611e6b1da94b95d46f8e7fe80be48f7a5ff8838375b08039514a399b11c2"
        "80735", 16),
    iqmp=int(
        "cd051cb0ea68b88765c041262ace2ec4db11dab14afd192742e34d5da3328637fabdf"
        "bae26e", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "4e1b470fe00642426f3808e74c959632dd67855a4c503c5b7876ccf4dc7f6a1a4"
            "9107b90d26daf0a7879a6858218345fbc6e59f01cd095ca5647c27c25265e6c47"
            "4fea89537191c7073d9d", 16),
    )
)

RSA_KEY_745 = RSAPrivateNumbers(
    p=int(
        "1c5a0cfe9a86debd19eca33ba961f15bc598aa7983a545ce775b933afc89eb51bcf90"
        "836257fdd060d4b383240241d", 16
    ),
    q=int(
        "fb2634f657f82ee6b70553382c4e2ed26b947c97ce2f0016f1b282cf2998184ad0527"
        "a9eead826dd95fe06b57a025", 16
    ),
    d=int(
        "402f30f976bc07d15ff0779abff127b20a8b6b1d0024cc2ad8b6762d38f174f81e792"
        "3b49d80bdbdd80d9675cbc7b2793ec199a0430eb5c84604dacfdb29259ae6a1a44676"
        "22f0b23d4cb0f5cb1db4b8173c8d9d3e57a74dbd200d2141", 16),
    dmp1=int(
        "e5e95b7751a6649f199be21bef7a51c9e49821d945b6fc5f538b4a670d8762c375b00"
        "8e70f31d52b3ea2bd14c3101", 16),
    dmq1=int(
        "12b85d5843645f72990fcf8d2f58408b34b3a3b9d9078dd527fceb5d2fb7839008092"
        "dd4aca2a1fb00542801dcef5", 16),
    iqmp=int(
        "5672740d947f621fc7969e3a44ec26736f3f819863d330e63e9409e139d20753551ac"
        "c16544dd2bdadb9dee917440", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "1bd085f92237774d34013b477ceebbb2f2feca71118db9b7429341477947e7b1d"
            "04e8c43ede3c52bb25781af58d4ff81289f301eac62dc3bcd7dafd7a4d5304e9f"
            "308e766952fbf2b62373e66611fa53189987dbef9f7243dcbbeb25831", 16),
    )
)

RSA_KEY_768 = RSAPrivateNumbers(
    p=int(
        "f80c0061b607f93206b68e208906498d68c6e396faf457150cf975c8f849848465869"
        "7ecd402313397088044c4c2071b", 16),
    q=int(
        "e5b5dbecc93c6d306fc14e6aa9737f9be2728bc1a326a8713d2849b34c1cb54c63468"
        "3a68abb1d345dbf15a3c492cf55", 16),
    d=int(
        "d44601442255ffa331212c60385b5e898555c75c0272632ff42d57c4b16ca97dbca9f"
        "d6d99cd2c9fd298df155ed5141b4be06c651934076133331d4564d73faed7ce98e283"
        "2f7ce3949bc183be7e7ca34f6dd04a9098b6c73649394b0a76c541", 16),
    dmp1=int(
        "a5763406fa0b65929661ce7b2b8c73220e43a5ebbfe99ff15ddf464fd238105ad4f2a"
        "c83818518d70627d8908703bb03", 16),
    dmq1=int(
        "cb467a9ef899a39a685aecd4d0ad27b0bfdc53b68075363c373d8eb2bed8eccaf3533"
        "42f4db735a9e087b7539c21ba9d", 16),
    iqmp=int(
        "5fe86bd3aee0c4d09ef11e0530a78a4534c9b833422813b5c934a450c8e564d8097a0"
        "6fd74f1ebe2d5573782093f587a", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "de92f1eb5f4abf426b6cac9dd1e9bf57132a4988b4ed3f8aecc15e251028bd6df"
            "46eb97c711624af7db15e6430894d1b640c13929329241ee094f5a4fe1a20bc9b"
            "75232320a72bc567207ec54d6b48dccb19737cf63acc1021abb337f19130f7",
            16),
    )
)

RSA_KEY_1024 = RSAPrivateNumbers(
    p=int(
        "ea4d9d9a1a068be44b9a5f8f6de0512b2c5ba1fb804a4655babba688e6e890b347c1a"
        "7426685a929337f513ae4256f0b7e5022d642237f960c5b24b96bee8e51", 16),
    q=int(
        "cffb33e400d6f08b410d69deb18a85cf0ed88fcca9f32d6f2f66c62143d49aff92c11"
        "4de937d4f1f62d4635ee89af99ce86d38a2b05310f3857c7b5d586ac8f9", 16),
    d=int(
        "3d12d46d04ce942fb99be7bf30587b8cd3e21d75a2720e7bda1b867f1d418d91d8b9f"
        "e1c00181fdde94f2faf33b4e6f800a1b3ae3b972ccb6d5079dcb6c794070ac8306d59"
        "c00b58b7a9a81122a6b055832de7c72334a07494d8e7c9fbeed2cc37e011d9e6bfc6e"
        "9bcddbef7f0f5771d9cf82cd4b268c97ec684575c24b6c881", 16),
    dmp1=int(
        "470f2b11257b7ec9ca34136f487f939e6861920ad8a9ae132a02e74af5dceaa5b4c98"
        "2949ccb44b67e2bcad2f58674db237fe250e0d62b47b28fa1dfaa603b41", 16),
    dmq1=int(
        "c616e8317d6b3ae8272973709b80e8397256697ff14ea03389de454f619f99915a617"
        "45319fefbe154ec1d49441a772c2f63f7d15c478199afc60469bfd0d561", 16),
    iqmp=int(
        "d15e7c9ad357dfcd5dbdc8427680daf1006761bcfba93a7f86589ad88832a8d564b1c"
        "d4291a658c96fbaea7ca588795820902d85caebd49c2d731e3fe0243130", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "be5aac07456d990133ebce69c06b48845b972ab1ad9f134bc5683c6b5489b5119"
            "ede07be3bed0e355d48e0dfab1e4fb5187adf42d7d3fb0401c082acb8481bf17f"
            "0e871f8877be04c3a1197d40aa260e2e0c48ed3fd2b93dc3fc0867591f67f3cd6"
            "0a77adee1d68a8c3730a5702485f6ac9ede7f0fd2918e037ee4cc1fc1b4c9",
            16),
    )
)

RSA_KEY_1025 = RSAPrivateNumbers(
    p=int(
        "18e9bfb7071725da04d31c103fa3563648c69def43a204989214eb57b0c8b299f9ef3"
        "5dda79a62d8d67fd2a9b69fbd8d0490aa2edc1e111a2b8eb7c737bb691a5", 16),
    q=int(
        "d8eccaeeb95815f3079d13685f3f72ca2bf2550b349518049421375df88ca9bbb4ba8"
        "cb0e3502203c9eeae174112509153445d251313e4711a102818c66fcbb7", 16),
    d=int(
        "fe9ac54910b8b1bc948a03511c54cab206a1d36d50d591124109a48abb7480977ccb0"
        "47b4d4f1ce7b0805df2d4fa3fe425f49b78535a11f4b87a4eba0638b3340c23d4e6b2"
        "1ecebe9d5364ea6ead2d47b27836019e6ecb407000a50dc95a8614c9d0031a6e3a524"
        "d2345cfb76e15c1f69d5ba35bdfb6ec63bcb115a757ef79d9", 16),
    dmp1=int(
        "18537e81006a68ea76d590cc88e73bd26bc38d09c977959748e5265c0ce21c0b5fd26"
        "53d975f97ef759b809f791487a8fff1264bf561627fb4527a3f0bbb72c85", 16),
    dmq1=int(
        "c807eac5a1f1e1239f04b04dd16eff9a00565127a91046fa89e1eb5d6301cace85447"
        "4d1f47b0332bd35b4214b66e9166953241538f761f30d969272ee214f17", 16),
    iqmp=int(
        "133aa74dd41fe70fa244f07d0c4091a22f8c8f0134fe6aea9ec8b55383b758fefe358"
        "2beec36eca91715eee7d21931f24fa9e97e8e3a50f9cd0f731574a5eafcc", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "151c44fed756370fb2d4a0e6ec7dcac84068ca459b6aaf22daf902dca72c77563"
            "bf276fe3523f38f5ddaf3ea9aa88486a9d8760ff732489075862bee0e599de5c5"
            "f509b4519f4f446521bad15cd279a498fe1e89107ce0d237e3103d7c5eb801666"
            "42e2924b152aebff97b71fdd2d68ebb45034cc784e2e822ff6d1edf98af3f3",
            16),
    )
)

RSA_KEY_1026 = RSAPrivateNumbers(
    p=int(
        "1fcbfb8719c5bdb5fe3eb0937c76bb096e750b9442dfe31d6a877a13aed2a6a4e9f79"
        "40f815f1c307dd6bc2b4b207bb6fe5be3a15bd2875a957492ce197cdedb1", 16),
    q=int(
        "1f704a0f6b8966dd52582fdc08227dd3dbaeaa781918b41144b692711091b4ca4eb62"
        "985c3513853828ce8739001dfba9a9a7f1a23cbcaf74280be925e2e7b50d", 16),
    d=int(
        "c67975e35a1d0d0b3ebfca736262cf91990cb31cf4ac473c0c816f3bc2720bcba2475"
        "e8d0de8535d257816c0fc53afc1b597eada8b229069d6ef2792fc23f59ffb4dc6c3d9"
        "0a3c462082025a4cba7561296dd3d8870c4440d779406f00879afe2c681e7f5ee055e"
        "ff829e6e55883ec20830c72300762e6e3a333d94b4dbe4501", 16),
    dmp1=int(
        "314730ca7066c55d086a9fbdf3670ef7cef816b9efea8b514b882ae9d647217cf41d7"
        "e9989269dc9893d02e315cb81f058c49043c2cac47adea58bdf5e20e841", 16),
    dmq1=int(
        "1da28a9d687ff7cfeebc2439240de7505a8796376968c8ec723a2b669af8ce53d9c88"
        "af18540bd78b2da429014923fa435f22697ac60812d7ca9c17a557f394cd", 16),
    iqmp=int(
        "727947b57b8a36acd85180522f1b381bce5fdbd962743b3b14af98a36771a80f58ddd"
        "62675d72a5935190da9ddc6fd6d6d5e9e9f805a2e92ab8d56b820493cdf", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "3e7a5e6483e55eb8b723f9c46732d21b0af9e06a4a1099962d67a35ee3f62e312"
            "9cfae6ab0446da18e26f33e1d753bc1cc03585c100cf0ab5ef056695706fc8b0c"
            "9c710cd73fe6e5beda70f515a96fabd3cc5ac49efcb2594b220ff3b603fcd927f"
            "6a0838ef04bf52f3ed9eab801f09e5aed1613ddeb946ed0fbb02060b3a36fd",
            16),
    )
)

RSA_KEY_1027 = RSAPrivateNumbers(
    p=int(
        "30135e54cfb072c3d3eaf2000f3ed92ceafc85efc867b9d4bf5612f2978c432040093"
        "4829f741c0f002b54af2a4433ff872b6321ef00ff1e72cba4e0ced937c7d", 16),
    q=int(
        "1d01a8aead6f86b78c875f18edd74214e06535d65da054aeb8e1851d6f3319b4fb6d8"
        "6b01e07d19f8261a1ded7dc08116345509ab9790e3f13e65c037e5bb7e27", 16),
    d=int(
        "21cf4477df79561c7818731da9b9c88cd793f1b4b8e175bd0bfb9c0941a4dc648ecf1"
        "6d96b35166c9ea116f4c2eb33ce1c231e641a37c25e54c17027bdec08ddafcb83642e"
        "795a0dd133155ccc5eed03b6e745930d9ac7cfe91f9045149f33295af03a2198c660f"
        "08d8150d13ce0e2eb02f21ac75d63b55822f77bd5be8d07619", 16),
    dmp1=int(
        "173fb695931e845179511c18b546b265cb79b517c135902377281bdf9f34205e1f399"
        "4603ad63e9f6e7885ea73a929f03fa0d6bed943051ce76cddde2d89d434d", 16),
    dmq1=int(
        "10956b387b2621327da0c3c8ffea2af8be967ee25163222746c28115a406e632a7f12"
        "5a9397224f1fa5c116cd3a313e5c508d31db2deb83b6e082d213e33f7fcf", 16),
    iqmp=int(
        "234f833949f2c0d797bc6a0e906331e17394fa8fbc8449395766d3a8d222cf6167c48"
        "8e7fe1fe9721d3e3b699a595c8e6f063d92bd840dbc84d763b2b37002109", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "57281707d7f9b1369c117911758980e32c05b133ac52c225bcf68b79157ff47ea"
            "0a5ae9f579ef1fd7e42937f921eb3123c4a045cc47a2159fbbf904783e654954c"
            "42294c30a95c15db7c7b91f136244e548f62474b137087346c5522e54f226f49d"
            "6c93bc58cb39972e41bde452bb3ae9d60eb93e5e1ce91d222138d9890c7d0b",
            16),
    )
)

RSA_KEY_1028 = RSAPrivateNumbers(
    p=int(
        "359d17378fae8e9160097daee78a206bd52efe1b757c12a6da8026cc4fc4bb2620f12"
        "b8254f4db6aed8228be8ee3e5a27ec7d31048602f01edb00befd209e8c75", 16),
    q=int(
        "33a2e70b93d397c46e63b273dcd3dcfa64291342a6ce896e1ec8f1c0edc44106550f3"
        "c06e7d3ca6ea29eccf3f6ab5ac6235c265313d6ea8e8767e6a343f616581", 16),
    d=int(
        "880640088d331aa5c0f4cf2887809a420a2bc086e671e6ffe4e47a8c80792c038a314"
        "9a8e45ef9a72816ab45b36e3af6800351067a6b2751843d4232413146bb575491463a"
        "8addd06ce3d1bcf7028ec6c5d938c545a20f0a40214b5c574ca7e840062b2b5f8ed49"
        "4b144bb2113677c4b10519177fee1d4f5fb8a1c159b0b47c01", 16),
    dmp1=int(
        "75f8c52dad2c1cea26b8bba63236ee4059489e3d2db766136098bcc6b67fde8f77cd3"
        "640035107bfb1ffc6480983cfb84fe0c3be008424ebc968a7db7e01f005", 16),
    dmq1=int(
        "3893c59469e4ede5cd0e6ff9837ca023ba9b46ff40c60ccf1bec10f7d38db5b1ba817"
        "6c41a3f750ec4203b711455aca06d1e0adffc5cffa42bb92c7cb77a6c01", 16),
    iqmp=int(
        "ad32aafae3c962ac25459856dc8ef1f733c3df697eced29773677f435d186cf759d1a"
        "5563dd421ec47b4d7e7f12f29647c615166d9c43fc49001b29089344f65", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "ad0696bef71597eb3a88e135d83c596930cac73868fbd7e6b2d64f34eea5c28cc"
            "e3510c68073954d3ba4deb38643e7a820a4cf06e75f7f82eca545d412bd637819"
            "45c28d406e95a6cced5ae924a8bfa4f3def3e0250d91246c269ec40c89c93a85a"
            "cd3770ba4d2e774732f43abe94394de43fb57f93ca25f7a59d75d400a3eff5",
            16),
    )
)

RSA_KEY_1029 = RSAPrivateNumbers(
    p=int(
        "66f33e513c0b6b6adbf041d037d9b1f0ebf8de52812a3ac397a963d3f71ba64b3ad04"
        "e4d4b5e377e6fa22febcac292c907dc8dcfe64c807fd9a7e3a698850d983", 16),
    q=int(
        "3b47a89a19022461dcc2d3c05b501ee76955e8ce3cf821beb4afa85a21a26fd7203db"
        "deb8941f1c60ada39fd6799f6c07eb8554113f1020460ec40e93cd5f6b21", 16),
    d=int(
        "280c42af8b1c719821f2f6e2bf5f3dd53c81b1f3e1e7cc4fce6e2f830132da0665bde"
        "bc1e307106b112b52ad5754867dddd028116cf4471bc14a58696b99524b1ad8f05b31"
        "cf47256e54ab4399b6a073b2c0452441438dfddf47f3334c13c5ec86ece4d33409056"
        "139328fafa992fb5f5156f25f9b21d3e1c37f156d963d97e41", 16),
    dmp1=int(
        "198c7402a4ec10944c50ab8488d7b5991c767e75eb2817bd427dff10335ae141fa2e8"
        "7c016dc22d975cac229b9ffdf7d943ddfd3a04b8bf82e83c3b32c5698b11", 16),
    dmq1=int(
        "15fd30c7687b68ef7c2a30cdeb913ec56c4757c218cf9a04d995470797ee5f3a17558"
        "fbb6d00af245d2631d893b382da48a72bc8a613024289895952ab245b0c1", 16),
    iqmp=int(
        "4f8fde17e84557a3f4e242d889e898545ab55a1a8e075c9bb0220173ccffe84659abe"
        "a235104f82e32750309389d4a52af57dbb6e48d831917b6efeb190176570", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "17d6e0a09aa5b2d003e51f43b9c37ffde74688f5e3b709fd02ef375cb6b8d15e2"
            "99a9f74981c3eeaaf947d5c2d64a1a80f5c5108a49a715c3f7be95a016b8d3300"
            "965ead4a4df76e642d761526803e9434d4ec61b10cb50526d4dcaef02593085de"
            "d8c331c1b27b200a45628403065efcb2c0a0ca1f75d648d40a007fbfbf2cae3",
            16),
    )
)

RSA_KEY_1030 = RSAPrivateNumbers(
    p=int(
        "6f4ac8a8172ef1154cf7f80b5e91de723c35a4c512860bfdbafcc3b994a2384bf7796"
        "3a2dd0480c7e04d5d418629651a0de8979add6f47b23da14c27a682b69c9", 16),
    q=int(
        "65a9f83e07dea5b633e036a9dccfb32c46bf53c81040a19c574c3680838fc6d28bde9"
        "55c0ff18b30481d4ab52a9f5e9f835459b1348bbb563ad90b15a682fadb3", 16),
    d=int(
        "290db707b3e1a96445ae8ea93af55a9f211a54ebe52995c2eb28085d1e3f09c986e73"
        "a00010c8e4785786eaaa5c85b98444bd93b585d0c24363ccc22c482e150a3fd900176"
        "86968e4fa20423ae72823b0049defceccb39bb34aa4ef64e6b14463b76d6a871c859e"
        "37285455b94b8e1527d1525b1682ac6f7c8fd79d576c55318c1", 16),
    dmp1=int(
        "23f7fa84010225dea98297032dac5d45745a2e07976605681acfe87e0920a8ab3caf5"
        "9d9602f3d63dc0584f75161fd8fff20c626c21c5e02a85282276a74628a9", 16),
    dmq1=int(
        "18ebb657765464a8aa44bf019a882b72a2110a77934c54915f70e6375088b10331982"
        "962bce1c7edd8ef9d3d95aa2566d2a99da6ebab890b95375919408d00f33", 16),
    iqmp=int(
        "3d59d208743c74054151002d77dcdfc55af3d41357e89af88d7eef2767be54c290255"
        "9258d85cf2a1083c035a33e65a1ca46dc8b706847c1c6434cef7b71a9dae", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "2c326574320818a6a8cb6b3328e2d6c1ba2a3f09b6eb2bc543c03ab18eb5efdaa"
            "8fcdbb6b4e12168304f587999f9d96a421fc80cb933a490df85d25883e6a88750"
            "d6bd8b3d4117251eee8f45e70e6daac7dbbd92a9103c623a09355cf00e3f16168"
            "e38b9c4cb5b368deabbed8df466bc6835eaba959bc1c2f4ec32a09840becc8b",
            16),
    )
)

RSA_KEY_1031 = RSAPrivateNumbers(
    p=int(
        "c0958c08e50137db989fb7cc93abf1984543e2f955d4f43fb2967f40105e79274c852"
        "293fa06ce63ca8436155e475ed6d1f73fea4c8e2516cc79153e3dc83e897", 16),
    q=int(
        "78cae354ea5d6862e5d71d20273b7cddb8cdfab25478fe865180676b04250685c4d03"
        "30c216574f7876a7b12dfe69f1661d3b0cea6c2c0dcfb84050f817afc28d", 16),
    d=int(
        "1d55cc02b17a5d25bfb39f2bc58389004d0d7255051507f75ef347cdf5519d1a00f4b"
        "d235ce4171bfab7bdb7a6dcfae1cf41433fb7da5923cc84f15a675c0b83492c95dd99"
        "a9fc157aea352ffdcbb5d59dbc3662171d5838d69f130678ee27841a79ef64f679ce9"
        "3821fa69c03f502244c04b737edad8967def8022a144feaab29", 16),
    dmp1=int(
        "5b1c2504ec3a984f86b4414342b5bcf59a0754f13adf25b2a0edbc43f5ba8c3cc061d"
        "80b03e5866d059968f0d10a98deaeb4f7830436d76b22cf41f2914e13eff", 16),
    dmq1=int(
        "6c361e1819691ab5d67fb2a8f65c958d301cdf24d90617c68ec7005edfb4a7b638cde"
        "79d4b61cfba5c86e8c0ccf296bc7f611cb8d4ae0e072a0f68552ec2d5995", 16),
    iqmp=int(
        "b7d61945fdc8b92e075b15554bab507fa8a18edd0a18da373ec6c766c71eece61136a"
        "84b90b6d01741d40458bfad17a9bee9d4a8ed2f6e270782dc3bf5d58b56e", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "5adebaa926ea11fb635879487fdd53dcfbb391a11ac7279bb3b4877c9b811370a"
            "9f73da0690581691626d8a7cf5d972cced9c2091ccf999024b23b4e6dc6d99f80"
            "a454737dec0caffaebe4a3fac250ed02079267c8f39620b5ae3e125ca35338522"
            "dc9353ecac19cb2fe3b9e3a9291619dbb1ea3a7c388e9ee6469fbf5fb22892b",
            16),
    )
)

RSA_KEY_1536 = RSAPrivateNumbers(
    p=int(
        "f1a65fa4e2aa6e7e2b560251e8a4cd65b625ad9f04f6571785782d1c213d91c961637"
        "0c572f2783caf2899f7fb690cf99a0184257fbd4b071b212c88fb348279a5387e61f1"
        "17e9c62980c45ea863fa9292087c0f66ecdcde6443d5a37268bf71", 16),
    q=int(
        "e54c2cbc3839b1da6ae6fea45038d986d6f523a3ae76051ba20583aab711ea5965cf5"
        "3cf54128cc9573f7460bba0fd6758a57aaf240c391790fb38ab473d83ef735510c53d"
        "1d10c31782e8fd7da42615e33565745c30a5e6ceb2a3ae0666cc35", 16),
    d=int(
        "7bcad87e23da2cb2a8c328883fabce06e1f8e9b776c8bf253ad9884e6200e3bd9bd3b"
        "a2cbe87d3854527bf005ba5d878c5b0fa20cfb0a2a42884ae95ca12bf7304285e9214"
        "5e992f7006c7c0ae839ad550da495b143bec0f4806c7f44caed45f3ccc6dc44cfaf30"
        "7abdb757e3d28e41c2d21366835c0a41e50a95af490ac03af061d2feb36ac0afb87be"
        "a13fb0f0c5a410727ebedb286c77f9469473fae27ef2c836da6071ef7efc1647f1233"
        "4009a89eecb09a8287abc8c2afd1ddd9a1b0641", 16),
    dmp1=int(
        "a845366cd6f9df1f34861bef7594ed025aa83a12759e245f58adaa9bdff9c3befb760"
        "75d3701e90038e888eec9bf092df63400152cb25fc07effc6c74c45f0654ccbde15cd"
        "90dd5504298a946fa5cf22a956072da27a6602e6c6e5c97f2db9c1", 16),
    dmq1=int(
        "28b0c1e78cdac03310717992d321a3888830ec6829978c048156152d805b4f8919c61"
        "70b5dd204e5ddf3c6c53bc6aff15d0bd09faff7f351b94abb9db980b31f150a6d7573"
        "08eb66938f89a5225cb4dd817a824c89e7a0293b58fc2eefb7e259", 16),
    iqmp=int(
        "6c1536c0e16e42a094b6caaf50231ba81916871497d73dcbbbd4bdeb9e60cae0413b3"
        "8143b5d680275b29ed7769fe5577e4f9b3647ddb064941120914526d64d80016d2eb7"
        "dc362da7c569623157f3d7cff8347f11494bf5c048d77e28d3f515", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "d871bb2d27672e54fc62c4680148cbdf848438da804e2c48b5a9c9f9daf6cc6e8"
            "ea7d2296f25064537a9a542aef3dd449ea75774238d4da02c353d1bee70013dcc"
            "c248ceef4050160705c188043c8559bf6dbfb6c4bb382eda4e9547575a8227d5b"
            "3c0a7088391364cf9f018d8bea053b226ec65e8cdbeaf48a071d0074860a734b1"
            "cb7d2146d43014b20776dea42f7853a54690e6cbbf3331a9f43763cfe2a51c329"
            "3bea3b2eebec0d8e43eb317a443afe541107d886e5243c096091543ae65", 16),
    )
)

RSA_KEY_2048 = RSAPrivateNumbers(
    p=int(
        "e14202e58c5f7446648d75e5dc465781f661f6b73000c080368afcfb21377f4ef19da"
        "845d4ef9bc6b151f6d9f34629103f2e57615f9ba0a3a2fbb035069e1d63b4bb0e78ad"
        "dad1ec3c6f87e25c877a1c4c1972098e09158ef7b9bc163852a18d44a70b7b31a03dc"
        "2614fd9ab7bf002cba79054544af3bfbdb6aed06c7b24e6ab", 16),
    q=int(
        "dbe2bea1ff92599bd19f9d045d6ce62250c05cfeac5117f3cf3e626cb696e3d886379"
        "557d5a57b7476f9cf886accfd40508a805fe3b45a78e1a8a125e516cda91640ee6398"
        "ec5a39d3e6b177ef12ab00d07907a17640e4ca454fd8487da3c4ffa0d5c2a5edb1221"
        "1c8e33c7ee9fa6753771fd111ec04b8317f86693eb2928c89", 16),
    d=int(
        "aef17f80f2653bc30539f26dd4c82ed6abc1d1b53bc0abcdbee47e9a8ab433abde865"
        "9fcfae1244d22de6ad333c95aee7d47f30b6815065ac3322744d3ea75058002cd1b29"
        "3141ee2a6dc682342432707080071bd2131d6262cab07871c28aa5238b87173fb78c3"
        "7f9c7bcd18c12e8971bb77fd9fa3e0792fec18d8d9bed0b03ba02b263606f24dbace1"
        "c8263ce2802a769a090e993fd49abc50c3d3c78c29bee2de0c98055d2f102f1c5684b"
        "8dddee611d5205392d8e8dd61a15bf44680972a87f040a611a149271eeb2573f8bf6f"
        "627dfa70e77def2ee6584914fa0290e041349ea0999cdff3e493365885b906cbcf195"
        "843345809a85098cca90fea014a21", 16),
    dmp1=int(
        "9ba56522ffcfa5244eae805c87cc0303461f82be29691b9a7c15a5a050df6c143c575"
        "7c288d3d7ab7f32c782e9d9fcddc10a604e6425c0e5d0e46069035d95a923646d276d"
        "d9d95b8696fa29ab0de18e53f6f119310f8dd9efca62f0679291166fed8cbd5f18fe1"
        "3a5f1ead1d71d8c90f40382818c18c8d069be793dbc094f69", 16),
    dmq1=int(
        "a8d4a0aaa2212ccc875796a81353da1fdf00d46676c88d2b96a4bfcdd924622d8e607"
        "f3ac1c01dda7ebfb0a97dd7875c2a7b2db6728fb827b89c519f5716fb3228f4121647"
        "04b30253c17de2289e9cce3343baa82eb404f789e094a094577a9b0c5314f1725fdf5"
        "8e87611ad20da331bd30b8aebc7dc97d0e9a9ba8579772c9", 16),
    iqmp=int(
        "17bd5ef638c49440d1853acb3fa63a5aca28cb7f94ed350db7001c8445da8943866a7"
        "0936e1ee2716c98b484e357cc054d82fbbd98d42f880695d38a1dd4eb096f629b9417"
        "aca47e6de5da9f34e60e8a0ffd7e35be74deeef67298d94b3e0db73fc4b7a4cb360c8"
        "9d2117a0bfd9434d37dc7c027d6b01e5295c875015510917d", 16),
    public_numbers=RSAPublicNumbers(
        e=65537,
        n=int(
            "c17afc7e77474caa5aa83036158a3ffbf7b5216851ba2230e5d6abfcc1c6cfef5"
            "9e923ea1330bc593b73802ab608a6e4a3306523a3116ba5aa3966145174e13b6c"
            "49e9b78062e449d72efb10fd49e91fa08b96d051e782e9f5abc5b5a6f7984827a"
            "db8e73da00f22b2efdcdb76eab46edad98ed65662743fdc6c0e336a5d0cdbaa7d"
            "c29e53635e24c87a5b2c4215968063cdeb68a972babbc1e3cff00fb9a80e372a4"
            "d0c2c920d1e8cee333ce470dc2e8145adb05bf29aee1d24f141e8cc784989c587"
            "fc6fbacd979f3f2163c1d7299b365bc72ffe2848e967aed1e48dcc515b3a50ed4"
            "de04fd053846ca10a223b10cc841cc80fdebee44f3114c13e886af583", 16),
    )
)
