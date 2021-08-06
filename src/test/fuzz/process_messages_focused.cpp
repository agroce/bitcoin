// Copyright (c) 2020-2021 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <consensus/consensus.h>
#include <net.h>
#include <net_processing.h>
#include <protocol.h>
#include <test/fuzz/FuzzedDataProvider.h>
#include <test/fuzz/fuzz.h>
#include <test/fuzz/util.h>
#include <test/util/mining.h>
#include <test/util/net.h>
#include <test/util/setup_common.h>
#include <test/util/validation.h>
#include <txorphanage.h>
#include <validation.h>
#include <validationinterface.h>

namespace {
const TestingSetup* g_setup;
} // namespace

void initialize_process_messages_focused()
{
    static const auto testing_setup = MakeNoLogFileContext<const TestingSetup>();
    g_setup = testing_setup.get();
    for (int i = 0; i < 2 * COINBASE_MATURITY; i++) {
        MineBlock(g_setup->m_node, CScript() << OP_TRUE);
    }
    SyncWithValidationInterfaceQueue();
}

FUZZ_TARGET_INIT(process_messages_focused, initialize_process_messages_focused)
{
    FuzzedDataProvider fuzzed_data_provider(buffer.data(), buffer.size());

    const int msg_types = (int32_t)getAllNetMessageTypes().size();
    std::vector<bool> swarm;
    size_t swarm_count = 0;
    for (int i = 0; i < msg_types; i++) {
        swarm.push_back(fuzzed_data_provider.ConsumeBool());
        if (swarm[i]) {
            swarm_count += 1;
        }
    }

    if (swarm_count == 0) {
        auto index_bytes = fuzzed_data_provider.ConsumeBytes<uint8_t>(1);
        size_t index = (index_bytes.size() == 0 ? 0 : index_bytes[0] % msg_types);
        swarm[index] = true;
    }

    ConnmanTestMsg& connman = *static_cast<ConnmanTestMsg*>(g_setup->m_node.connman.get());
    TestChainState& chainstate = *static_cast<TestChainState*>(&g_setup->m_node.chainman->ActiveChainstate());
    SetMockTime(1610000000); // any time to successfully reset ibd
    chainstate.ResetIbd();

    std::vector<CNode*> peers;
    const auto num_peers_to_add = fuzzed_data_provider.ConsumeIntegralInRange(1, 3);
    for (int i = 0; i < num_peers_to_add; ++i) {
        peers.push_back(ConsumeNodeAsUniquePtr(fuzzed_data_provider, i).release());
        CNode& p2p_node = *peers.back();

        const bool successfully_connected{fuzzed_data_provider.ConsumeBool()};
        p2p_node.fSuccessfullyConnected = successfully_connected;
        p2p_node.fPauseSend = false;
        g_setup->m_node.peerman->InitializeNode(&p2p_node);
        FillNode(fuzzed_data_provider, p2p_node, /* init_version */ successfully_connected);

        connman.AddTestNode(p2p_node);
    }

    while (fuzzed_data_provider.ConsumeBool()) {
        auto index_bytes = fuzzed_data_provider.ConsumeBytes<uint8_t>(1);
        size_t index = (index_bytes.size() == 0 ? 0 : index_bytes[0] % msg_types);
	
        while (!swarm[index]) {
            index = (index + 1) % msg_types;
        }
        const std::string random_message_type{getAllNetMessageTypes()[index]};

        const auto mock_time = ConsumeTime(fuzzed_data_provider);
        SetMockTime(mock_time);

        CSerializedNetMsg net_msg;
        net_msg.m_type = random_message_type;
        net_msg.data = ConsumeRandomLengthByteVector(fuzzed_data_provider);

        CNode& random_node = *PickValue(fuzzed_data_provider, peers);

        (void)connman.ReceiveMsgFrom(random_node, net_msg);
        random_node.fPauseSend = false;

        try {
            connman.ProcessMessagesOnce(random_node);
        } catch (const std::ios_base::failure&) {
        }
        {
            LOCK(random_node.cs_sendProcessing);
            g_setup->m_node.peerman->SendMessages(&random_node);
        }
    }
    SyncWithValidationInterfaceQueue();
    g_setup->m_node.connman->StopNodes();
}
